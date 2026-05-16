#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: notification_info
short_description: List PagerDuty notifications
description:
  - Retrieve notifications with optional date range and filter.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  since:
    description: Start of date range (ISO 8601). Required.
    type: str
    required: true
  until:
    description: End of date range (ISO 8601). Required.
    type: str
    required: true
  filter_type:
    description: Filter by notification type.
    type: str
    choices: [assignee, responder]
  include:
    description: Additional data to include.
    type: list
    elements: str
    choices: [users]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get notifications for a date range
  pagerduty.pagerduty.notification_info:
    since: "2024-01-01T00:00:00Z"
    until: "2024-01-02T00:00:00Z"
  register: result

- name: Get assignee notifications with user details
  pagerduty.pagerduty.notification_info:
    since: "2024-01-01T00:00:00Z"
    until: "2024-01-02T00:00:00Z"
    filter_type: assignee
    include: [users]
  register: result
'''

RETURN = r'''
notifications:
  description: List of notifications.
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
            since=dict(type='str', required=True),
            until=dict(type='str', required=True),
            filter_type=dict(type='str', choices=['assignee', 'responder']),
            include=dict(type='list', elements='str', choices=['users']),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        qp = {
            'since': params['since'],
            'until': params['until'],
        }
        if params['filter_type']:
            qp['filter'] = params['filter_type']
        if params['include']:
            qp['include[]'] = ','.join(params['include'])
        notifications = client.list_all('/notifications', 'notifications', params=qp)
        module.exit_json(changed=False, notifications=notifications)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
