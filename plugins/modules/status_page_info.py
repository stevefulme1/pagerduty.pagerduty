#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: status_page_info
short_description: Get PagerDuty status page info
description:
  - Retrieve a single status page by ID or list all status pages.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific status page to retrieve.
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
- name: Get a specific status page
  pagerduty.pagerduty.status_page_info:
    id: PSTATPG01
  register: result

- name: List all status pages
  pagerduty.pagerduty.status_page_info:
  register: result

- name: List status pages with pagination
  pagerduty.pagerduty.status_page_info:
    limit: 10
    offset: 0
  register: result
'''

RETURN = r'''
status_pages:
  description: List of status pages matching the query.
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
            page = client.get('/status_pages/{0}'.format(params['id']))
            module.exit_json(changed=False, status_pages=[page.get('status_page', page)])
        else:
            qp = {}
            if params['limit']:
                qp['limit'] = params['limit']
            if params['offset']:
                qp['offset'] = params['offset']
            pages = client.list_all('/status_pages', 'status_pages', params=qp or None)
            module.exit_json(changed=False, status_pages=pages)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
