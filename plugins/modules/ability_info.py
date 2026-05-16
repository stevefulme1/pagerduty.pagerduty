#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ability_info
short_description: List PagerDuty account abilities
description:
  - Retrieve all abilities (features) enabled for the account.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: List all account abilities
  pagerduty.pagerduty.ability_info:
  register: result
'''

RETURN = r'''
abilities:
  description: List of account abilities.
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
        result = client.get('/abilities')
        abilities = result.get('abilities', [])
        module.exit_json(changed=False, abilities=abilities)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
