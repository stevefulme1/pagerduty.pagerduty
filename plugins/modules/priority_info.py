#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: priority_info
short_description: List PagerDuty priorities
description:
  - Retrieve all priorities configured in the account.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: List all priorities
  pagerduty.pagerduty.priority_info:
  register: result
'''

RETURN = r'''
priorities:
  description: List of priorities.
  type: list
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyClient, PagerDutyError,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(**PAGERDUTY_COMMON_ARGS),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)

    try:
        result = client.get('/priorities')
        priorities = result.get('priorities', [])
        module.exit_json(changed=False, priorities=priorities)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
