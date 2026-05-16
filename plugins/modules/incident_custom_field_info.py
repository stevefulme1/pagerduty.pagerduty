#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incident_custom_field_info
short_description: List PagerDuty incident custom fields
description:
  - Retrieve a single custom field by ID or name, or list all custom fields.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific custom field to retrieve.
    type: str
  name:
    description: Filter custom fields by exact name match.
    type: str
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: List all incident custom fields
  pagerduty.pagerduty.incident_custom_field_info:
  register: result

- name: Get a specific custom field
  pagerduty.pagerduty.incident_custom_field_info:
    id: PFIELD01
  register: result
'''

RETURN = r'''
fields:
  description: List of incident custom fields.
  type: list
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyClient, PagerDutyError,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            id=dict(type='str'),
            name=dict(type='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        if params['id']:
            field = client.get('/incidents/custom_fields/{0}'.format(params['id']))
            module.exit_json(changed=False, fields=[field.get('field', field)])
        else:
            result = client.get('/incidents/custom_fields')
            fields = result.get('fields', [])
            if params['name']:
                fields = [f for f in fields if f.get('name') == params['name']]
            module.exit_json(changed=False, fields=fields)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
