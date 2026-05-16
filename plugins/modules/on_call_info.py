#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: on_call_info
short_description: Get current PagerDuty on-call entries
description:
  - Retrieve current on-call entries with optional filters.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  schedule_ids:
    description: Filter by schedule IDs.
    type: list
    elements: str
  user_ids:
    description: Filter by user IDs.
    type: list
    elements: str
  escalation_policy_ids:
    description: Filter by escalation policy IDs.
    type: list
    elements: str
  since:
    description: Start of date range (ISO 8601).
    type: str
  until:
    description: End of date range (ISO 8601).
    type: str
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get all current on-calls
  pagerduty.pagerduty.on_call_info:
  register: result

- name: Get on-calls for a specific schedule
  pagerduty.pagerduty.on_call_info:
    schedule_ids: ["PSCHED01"]
  register: result

- name: Get on-calls for a specific user
  pagerduty.pagerduty.on_call_info:
    user_ids: ["PUSER01"]
  register: result
'''

RETURN = r'''
oncalls:
  description: List of on-call entries.
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
            schedule_ids=dict(type='list', elements='str'),
            user_ids=dict(type='list', elements='str'),
            escalation_policy_ids=dict(type='list', elements='str'),
            since=dict(type='str'),
            until=dict(type='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        qp = {}
        if params['schedule_ids']:
            qp['schedule_ids[]'] = ','.join(params['schedule_ids'])
        if params['user_ids']:
            qp['user_ids[]'] = ','.join(params['user_ids'])
        if params['escalation_policy_ids']:
            qp['escalation_policy_ids[]'] = ','.join(params['escalation_policy_ids'])
        if params['since']:
            qp['since'] = params['since']
        if params['until']:
            qp['until'] = params['until']
        oncalls = client.list_all('/oncalls', 'oncalls', params=qp or None)
        module.exit_json(changed=False, oncalls=oncalls)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
