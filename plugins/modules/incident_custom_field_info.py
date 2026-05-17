#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
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

  limit:
    description:
      - Maximum number of results to return per request.
      - PagerDuty API default is 25, max is 100.
    type: int
    default: 100
  offset:
    description:
      - Pagination offset (number of records to skip).
      - Used for manual pagination through large result sets.
    type: int
    default: 0
  max_results:
    description:
      - Maximum total number of results to return across all pages.
      - Set to 0 for no limit.
    type: int
    default: 1000
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
            limit=dict(type='int', default=100),
            offset=dict(type='int', default=0),
            max_results=dict(type='int', default=1000),
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
