#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: escalation_policy_info
short_description: List or get PagerDuty escalation policies
description:
  - Retrieve a single escalation policy by ID or name, or list all with optional filters.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific escalation policy to retrieve.
    type: str
  name:
    description: Filter escalation policies by exact name match.
    type: str
  user_ids:
    description: List of user IDs to filter by.
    type: list
    elements: str
  team_ids:
    description: List of team IDs to filter by.
    type: list
    elements: str

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
- name: Get a specific escalation policy
  pagerduty.pagerduty.escalation_policy_info:
    id: PPOLICY1
  register: result

- name: Find escalation policies for a team
  pagerduty.pagerduty.escalation_policy_info:
    team_ids: ["PTEAM01"]
  register: result
'''

RETURN = r'''
escalation_policies:
  description: List of escalation policies matching the query.
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
            user_ids=dict(type='list', elements='str'),
            team_ids=dict(type='list', elements='str'),
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
            ep = client.get('/escalation_policies/{0}'.format(params['id']))
            module.exit_json(changed=False, escalation_policies=[ep.get('escalation_policy', ep)])
        else:
            qp = {}
            if params['name']:
                qp['query'] = params['name']
            if params['user_ids']:
                qp['user_ids[]'] = ','.join(params['user_ids'])
            if params['team_ids']:
                qp['team_ids[]'] = ','.join(params['team_ids'])
            if params.get('limit'):
                qp['limit'] = params['limit']
            if params.get('offset'):
                qp['offset'] = params['offset']
            eps = client.list_all('/escalation_policies', 'escalation_policies', params=qp or None)
            if params['name']:
                eps = [e for e in eps if e.get('name') == params['name']]
            module.exit_json(changed=False, escalation_policies=eps)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
