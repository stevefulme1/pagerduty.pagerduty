#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incident_custom_field
short_description: Manage PagerDuty incident custom fields
description:
  - Create, update, and delete custom fields on incidents in PagerDuty.
version_added: "1.0.0"
author: PagerDuty Ansible Collection Authors
options:
  name:
    description: The API name of the custom field (machine-readable).
    type: str
    required: true
  display_name:
    description: The human-readable display name of the field.
    type: str
    required: true
  data_type:
    description: The data type of the field.
    type: str
    required: true
    choices: [string, integer, float, boolean, datetime]
  field_type:
    description: Whether the field holds a single value or multiple values.
    type: str
    default: single_value
    choices: [single_value, multi_value]
  description:
    description: A description of the custom field.
    type: str
    default: ''
  default_value:
    description: The default value for the field.
    type: raw
  field_options:
    description: List of allowed values for multi_value field types.
    type: list
    elements: str
    default: []
  state:
    description: Whether the custom field should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a string custom field
  pagerduty.pagerduty.incident_custom_field:
    api_token: "{{ pd_token }}"
    name: "environment"
    display_name: "Environment"
    data_type: string
    field_type: single_value
    description: "The affected environment"
    state: present

- name: Create a multi-value custom field
  pagerduty.pagerduty.incident_custom_field:
    api_token: "{{ pd_token }}"
    name: "regions"
    display_name: "Affected Regions"
    data_type: string
    field_type: multi_value
    field_options:
      - us-east-1
      - us-west-2
      - eu-west-1
    state: present

- name: Delete a custom field
  pagerduty.pagerduty.incident_custom_field:
    api_token: "{{ pd_token }}"
    name: "old_field"
    display_name: "Old Field"
    data_type: string
    state: absent
'''

RETURN = r'''
field:
  description: The custom field object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)

API_PATH = '/incidents/custom_fields'
RESOURCE_KEY = 'field'
LIST_KEY = 'fields'


def find_field_by_name(pd, name):
    """Find a custom field by its API name."""
    try:
        fields = pd.client.list_all(API_PATH, LIST_KEY)
    except PagerDutyError:
        return None
    for field in fields:
        if field.get('name') == name:
            return field
    return None


def build_payload(module):
    """Build the custom field payload."""
    data = {
        'name': module.params['name'],
        'display_name': module.params['display_name'],
        'data_type': module.params['data_type'],
        'field_type': module.params['field_type'],
        'description': module.params['description'],
    }
    if module.params['default_value'] is not None:
        data['default_value'] = module.params['default_value']
    if module.params['field_options']:
        data['field_options'] = [
            {'data': {'data_type': module.params['data_type'], 'value': opt}}
            for opt in module.params['field_options']
        ]
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        display_name=dict(type='str', required=True),
        data_type=dict(type='str', required=True, choices=['string', 'integer', 'float', 'boolean', 'datetime']),
        field_type=dict(type='str', default='single_value', choices=['single_value', 'multi_value']),
        description=dict(type='str', default=''),
        default_value=dict(type='raw'),
        field_options=dict(type='list', elements='str', default=[]),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        existing = find_field_by_name(pd, module.params['name'])

        if state == 'present':
            payload = build_payload(module)
            if existing:
                if not pd.check_mode:
                    result = pd.client.put(
                        '{0}/{1}'.format(API_PATH, existing['id']),
                        {RESOURCE_KEY: payload},
                    )
                    pd.result[RESOURCE_KEY] = result.get(RESOURCE_KEY, result)
                else:
                    pd.result[RESOURCE_KEY] = existing
                pd.result['changed'] = True
            else:
                if not pd.check_mode:
                    result = pd.client.post(API_PATH, {RESOURCE_KEY: payload})
                    pd.result[RESOURCE_KEY] = result.get(RESOURCE_KEY, result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete('{0}/{1}'.format(API_PATH, existing['id']))
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
