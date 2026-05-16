#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: escalation_policy
short_description: Manage PagerDuty escalation policies
description:
  - Create, update, or delete PagerDuty escalation policies.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  name:
    description: The name of the escalation policy.
    type: str
    required: true
  description:
    description: A description for the escalation policy.
    type: str
  num_loops:
    description: Number of times the escalation policy will repeat after reaching the end.
    type: int
    default: 0
  on_call_handoff_notifications:
    description: How on-call handoff notifications are sent.
    type: str
    choices: [if_has_services, always]
  rules:
    description: >
      List of escalation rules. Each rule is a dict with escalation_delay_in_minutes
      and targets (list of dicts with type and id).
    type: list
    elements: dict
  state:
    description: Whether the escalation policy should exist.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create an escalation policy
  pagerduty.pagerduty.escalation_policy:
    name: Engineering On-Call
    description: Primary engineering escalation
    num_loops: 2
    rules:
      - escalation_delay_in_minutes: 30
        targets:
          - type: user_reference
            id: PUSER123
    api_token: "{{ pagerduty_token }}"

- name: Delete an escalation policy
  pagerduty.pagerduty.escalation_policy:
    name: Engineering On-Call
    state: absent
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
escalation_policy:
  description: The escalation policy object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def build_policy_data(module):
    data = {
        'name': module.params['name'],
        'type': 'escalation_policy',
        'num_loops': module.params.get('num_loops', 0),
    }
    if module.params.get('description') is not None:
        data['description'] = module.params['description']
    if module.params.get('on_call_handoff_notifications') is not None:
        data['on_call_handoff_notifications'] = module.params['on_call_handoff_notifications']
    if module.params.get('rules') is not None:
        data['escalation_rules'] = module.params['rules']
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str'),
        num_loops=dict(type='int', default=0),
        on_call_handoff_notifications=dict(type='str', choices=['if_has_services', 'always']),
        rules=dict(type='list', elements='dict'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        if module.params['state'] == 'present':
            pd.ensure_present(
                resource_key='escalation_policy',
                find_path='/escalation_policies',
                find_key='escalation_policies',
                create_path='/escalation_policies',
                create_data=build_policy_data(module),
                update_path_tmpl='/escalation_policies/{id}',
                update_data_fn=lambda: build_policy_data(module),
                compare_keys=['name', 'description', 'num_loops', 'on_call_handoff_notifications',
                              'escalation_rules'],
            )
        else:
            pd.ensure_absent(
                resource_key='escalation_policy',
                find_path='/escalation_policies',
                find_key='escalation_policies',
                delete_path_tmpl='/escalation_policies/{id}',
            )
        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
