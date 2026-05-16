#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event_orchestration_global_rule
short_description: Manage PagerDuty event orchestration global rules
description:
  - Configure global rules for a PagerDuty event orchestration.
  - Global rules apply transformations before routing.
version_added: "1.0.0"
author: "PagerDuty Collection Authors"
options:
  orchestration:
    description: Event orchestration name or ID.
    type: str
    required: true
  sets:
    description:
      - List of rule sets. Each set has an C(id) and C(rules) list.
      - Each rule has optional C(label), C(conditions), and C(actions).
      - Actions can include severity, priority, annotations, variables, and extractions.
    type: list
    elements: dict
    required: true
  state:
    description: Desired state.
    type: str
    choices: [present]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Configure global orchestration rules
  pagerduty.pagerduty.event_orchestration_global_rule:
    api_token: "{{ pd_token }}"
    orchestration: "Production Orchestration"
    sets:
      - id: start
        rules:
          - label: "Set severity for critical alerts"
            conditions:
              - expression: "event.severity matches 'critical'"
            actions:
              severity: critical
              priority: P1
'''

RETURN = r'''
global:
  description: The global rules configuration object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_orchestration(client, value):
    if value.startswith('P') and len(value) >= 7:
        return value
    found = client.find_by_name('/event_orchestrations', 'orchestrations', value)
    if not found:
        raise PagerDutyError('Could not find orchestration "{0}"'.format(value))
    return found['id']


def build_sets(sets_param):
    result_sets = []
    for s in sets_param:
        rule_set = {'id': s.get('id', 'start'), 'rules': []}
        for rule in s.get('rules', []):
            r = {}
            if rule.get('label'):
                r['label'] = rule['label']
            if rule.get('conditions'):
                r['conditions'] = rule['conditions']
            actions = rule.get('actions', {})
            if isinstance(actions, dict):
                r['actions'] = actions
            else:
                r['actions'] = {}
            rule_set['rules'].append(r)
        result_sets.append(rule_set)
    return result_sets


def main():
    argument_spec = dict(
        orchestration=dict(type='str', required=True),
        sets=dict(type='list', elements='dict', required=True),
        state=dict(type='str', default='present', choices=['present']),
        **PAGERDUTY_COMMON_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    pd = PagerDutyModule(module)

    try:
        orch_id = resolve_orchestration(pd.client, module.params['orchestration'])
        path = '/event_orchestrations/{0}/global'.format(orch_id)

        current = pd.client.get(path)
        desired_sets = build_sets(module.params['sets'])
        desired = {'orchestration_path': {'sets': desired_sets}}

        current_sets = current.get('orchestration_path', {}).get('sets', [])
        if current_sets != desired_sets:
            if not pd.check_mode:
                result = pd.client.put(path, desired)
                pd.result['global'] = result
            pd.result['changed'] = True
        else:
            pd.result['global'] = current

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
