#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: business_service_info
short_description: List or get PagerDuty business services
description:
  - Retrieve a single business service by ID or name, or list all.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific business service to retrieve.
    type: str
  name:
    description: Filter business services by exact name match.
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
- name: Get a specific business service
  pagerduty.pagerduty.business_service_info:
    id: PBSVC01
  register: result

- name: List all business services
  pagerduty.pagerduty.business_service_info:
  register: result
'''

RETURN = r'''
business_services:
  description: List of business services matching the query.
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
            bs = client.get('/business_services/{0}'.format(params['id']))
            module.exit_json(changed=False, business_services=[bs.get('business_service', bs)])
        else:
            if params.get('limit'):
                qp['limit'] = params['limit']
            if params.get('offset'):
                qp['offset'] = params['offset']
            services = client.list_all('/business_services', 'business_services')
            if params['name']:
                services = [s for s in services if s.get('name') == params['name']]
            module.exit_json(changed=False, business_services=services)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
