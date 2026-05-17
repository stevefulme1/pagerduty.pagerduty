#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event_orchestration_info
short_description: List or get PagerDuty event orchestrations
description:
  - Retrieve a single event orchestration by ID or name, or list all.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific event orchestration to retrieve.
    type: str
  name:
    description: Filter event orchestrations by exact name match.
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
- name: Get a specific event orchestration
  pagerduty.pagerduty.event_orchestration_info:
    id: PORCH01
  register: result

- name: Find an event orchestration by name
  pagerduty.pagerduty.event_orchestration_info:
    name: Production Events
  register: result
'''

RETURN = r'''
event_orchestrations:
  description: List of event orchestrations matching the query.
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
            orch = client.get('/event_orchestrations/{0}'.format(params['id']))
            module.exit_json(changed=False, event_orchestrations=[orch.get('orchestration', orch)])
        else:
            qp = {}
            if params.get('limit'):
                qp['limit'] = params['limit']
            if params.get('offset'):
                qp['offset'] = params['offset']
            orchs = client.list_all('/event_orchestrations', 'orchestrations', params=qp or None)
            if params['name']:
                orchs = [o for o in orchs if o.get('name') == params['name']]
            module.exit_json(changed=False, event_orchestrations=orchs)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
