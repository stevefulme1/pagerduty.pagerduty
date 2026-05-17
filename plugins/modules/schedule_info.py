#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: schedule_info
short_description: List or get PagerDuty schedules
description:
  - Retrieve a single schedule by ID or name, or list all schedules.
  - When retrieving by ID with since/until, returns the rendered schedule.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific schedule to retrieve.
    type: str
  name:
    description: Filter schedules by exact name match.
    type: str
  since:
    description: Start of date range for rendered schedule (ISO 8601).
    type: str
  until:
    description: End of date range for rendered schedule (ISO 8601).
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
- name: Get a specific schedule with rendered entries
  pagerduty.pagerduty.schedule_info:
    id: PSCHED01
    since: "2024-01-01T00:00:00Z"
    until: "2024-01-07T00:00:00Z"
  register: result

- name: List all schedules
  pagerduty.pagerduty.schedule_info:
  register: result
'''

RETURN = r'''
schedules:
  description: List of schedules matching the query.
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
            since=dict(type='str'),
            until=dict(type='str'),
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
            qp = {}
            if params['since']:
                qp['since'] = params['since']
            if params['until']:
                qp['until'] = params['until']
            sched = client.get('/schedules/{0}'.format(params['id']), params=qp or None)
            module.exit_json(changed=False, schedules=[sched.get('schedule', sched)])
        else:
            qp = {}
            if params['name']:
                qp['query'] = params['name']
            if params.get('limit'):
                qp['limit'] = params['limit']
            if params.get('offset'):
                qp['offset'] = params['offset']
            schedules = client.list_all('/schedules', 'schedules', params=qp or None)
            if params['name']:
                schedules = [s for s in schedules if s.get('name') == params['name']]
            module.exit_json(changed=False, schedules=schedules)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
