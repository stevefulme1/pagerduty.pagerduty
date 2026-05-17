#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
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
