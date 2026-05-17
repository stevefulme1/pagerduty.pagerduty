#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: custom_field_schema
short_description: Manage PagerDuty incident custom field schemas
description:
  - Create, update, and delete custom field schemas in PagerDuty.
  - Field schemas define how custom fields are organized and assigned.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  id:
    description: The ID of the schema to update or delete.
    type: str
  title:
    description: The title of the field schema.
    type: str
    required: true
  description:
    description: A description of the field schema.
    type: str
    default: ''
  field_ids:
    description: List of custom field IDs to include in the schema.
    type: list
    elements: str
    default: []
  state:
    description: Whether the schema should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a custom field schema
  pagerduty.pagerduty.custom_field_schema:
    api_token: "{{ pd_token }}"
    title: "Incident Classification"
    description: "Fields for classifying incidents"
    field_ids:
      - PFIELD01
      - PFIELD02
    state: present

- name: Delete a custom field schema
  pagerduty.pagerduty.custom_field_schema:
    api_token: "{{ pd_token }}"
    title: "Old Schema"
    id: PSCHEMA01
    state: absent
'''

RETURN = r'''
schema:
  description: The custom field schema object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)

API_PATH = '/incidents/custom_fields/schemas'
RESOURCE_KEY = 'schema'
LIST_KEY = 'schemas'


def find_by_title(pd, title):
    """Find a schema by title."""
    try:
        schemas = pd.client.list_all(API_PATH, LIST_KEY)
    except PagerDutyError:
        return None
    for schema in schemas:
        if schema.get('title') == title:
            return schema
    return None


def build_payload(module):
    """Build the schema payload."""
    data = {
        'title': module.params['title'],
        'description': module.params['description'],
    }
    if module.params['field_ids']:
        data['field_configurations'] = [
            {'field': {'id': fid}} for fid in module.params['field_ids']
        ]
    return data


def main():
    argument_spec = dict(
        id=dict(type='str'),
        title=dict(type='str', required=True),
        description=dict(type='str', default=''),
        field_ids=dict(type='list', elements='str', default=[]),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        existing = None
        if module.params['id']:
            existing = pd.client.find_by_id('{0}/{1}'.format(API_PATH, module.params['id']), RESOURCE_KEY)
        else:
            existing = find_by_title(pd, module.params['title'])

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
