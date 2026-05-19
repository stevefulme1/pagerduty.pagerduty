#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: user_notification_rule_info
short_description: List notification rules for a PagerDuty user
description:
  - Retrieve information about PagerDuty notification rules.
  - This is a read-only module that does not modify any resources.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  user_id:
    description: The ID of the user.
    type: str
    required: true
  id:
    description: The ID of a specific notification rule.
    type: str
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: List all notification rules
  pagerduty.pagerduty.user_notification_rule_info:
    user_id: EXAMPLE_ID
  register: result

- name: Get a specific notification rule
  pagerduty.pagerduty.user_notification_rule_info:
    user_id: EXAMPLE_ID
    id: PABC123
  register: result
'''

RETURN = r'''
notification_rules:
  description: List of notification rules matching the query.
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
            user_id=dict(type='str', required=True),
            id=dict(type='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        if params['id']:
            result = client.get('/users/{user_id}/notification_rules/' + params['id'])
            module.exit_json(changed=False, count=1, notification_rules=[result.get('notification_rule', result)])
        else:
            qp = {}
            data = client.list_all('/users/' + params['user_id'] + '/notification_rules', 'notification_rules',
                params=qp or None)
            module.exit_json(changed=False, notification_rules=data, count=len(data))
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
