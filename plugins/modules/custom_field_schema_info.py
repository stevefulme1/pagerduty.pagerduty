#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: custom_field_schema_info
short_description: Get PagerDuty custom field schema info
description:
  - Retrieve a single custom field schema by ID or list all schemas.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific schema to retrieve.
    type: str
  limit:
    description: Maximum number of results to return per page.
    type: int
    default: 25
  offset:
    description: Offset for pagination.
    type: int
    default: 0
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get a specific schema
  pagerduty.pagerduty.custom_field_schema_info:
    id: PSCHEMA01
  register: result

- name: List all schemas
  pagerduty.pagerduty.custom_field_schema_info:
  register: result

- name: List schemas with pagination
  pagerduty.pagerduty.custom_field_schema_info:
    limit: 10
    offset: 0
  register: result
'''

RETURN = r'''
schemas:
  description: List of custom field schemas.
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
            limit=dict(type='int', default=25),
            offset=dict(type='int', default=0),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        if params['id']:
            schema = client.get('/incidents/custom_fields/schemas/{0}'.format(params['id']))
            module.exit_json(changed=False, schemas=[schema.get('schema', schema)])
        else:
            qp = {}
            if params['limit']:
                qp['limit'] = params['limit']
            if params['offset']:
                qp['offset'] = params['offset']
            schemas = client.list_all('/incidents/custom_fields/schemas', 'schemas', params=qp or None)
            module.exit_json(changed=False, schemas=schemas)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
