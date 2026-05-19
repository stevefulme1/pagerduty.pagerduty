#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: extension_info
short_description: List or get PagerDuty extensions
description:
  - Retrieve information about PagerDuty extensions.
  - This is a read-only module that does not modify any resources.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific extension to retrieve.
    type: str
  extension_schema_id:
    description: Filter by extension schema ID.
    type: str
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: List all extensions
  pagerduty.pagerduty.extension_info:
  register: result

- name: Get a specific extension
  pagerduty.pagerduty.extension_info:
    id: PABC123
  register: result
'''

RETURN = r'''
extensions:
  description: List of extensions matching the query.
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the resource.
      type: str
      returned: always
    type:
      description: The PagerDuty resource type.
      type: str
      returned: always
    summary:
      description: A short summary of the resource.
      type: str
      returned: when available
    self:
      description: The API URL for this resource.
      type: str
      returned: always
    html_url:
      description: The URL to view this resource in the PagerDuty web UI.
      type: str
      returned: when available
count:
  description: Number of results returned.
  type: int
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
            extension_schema_id=dict(type='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        if params['id']:
            result = client.get('/extensions/' + params['id'])
            module.exit_json(changed=False, count=1, extensions=[result.get('extension', result)])
        else:
            qp = {}
            if params['extension_schema_id']:
                qp['query'] = params['extension_schema_id']
            data = client.list_all('/extensions', 'extensions', params=qp or None)
            module.exit_json(changed=False, extensions=data, count=len(data))
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
