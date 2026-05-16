#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: automation_action_runner
short_description: Manage PagerDuty automation action runners
description:
  - Create, update, and delete automation action runners in PagerDuty.
  - Runners are execution environments that run automation actions.
version_added: "1.0.0"
author: Ansible Ansible PagerDuty Collection Authors (@ansible-collections) (@ansible-collections)
options:
  name:
    description: The name of the runner.
    type: str
    required: true
  description:
    description: A description of the runner.
    type: str
    default: ''
  runner_type:
    description: The type of runner.
    type: str
    required: true
    choices: [sidecar, runbook]
  teams:
    description: List of team IDs associated with this runner.
    type: list
    elements: str
    default: []
  state:
    description: Whether the runner should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a sidecar runner
  pagerduty.pagerduty.automation_action_runner:
    api_token: "{{ pd_token }}"
    name: "Production Runner"
    description: "Runner in the production environment"
    runner_type: sidecar
    teams:
      - PXXXXXX
    state: present

- name: Create a runbook runner
  pagerduty.pagerduty.automation_action_runner:
    api_token: "{{ pd_token }}"
    name: "Runbook Runner"
    runner_type: runbook
    state: present

- name: Delete a runner
  pagerduty.pagerduty.automation_action_runner:
    api_token: "{{ pd_token }}"
    name: "Old Runner"
    runner_type: sidecar
    state: absent
'''

RETURN = r'''
runner:
  description: The automation action runner object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)

API_PATH = '/automation_actions/runners'
RESOURCE_KEY = 'runner'
LIST_KEY = 'runners'


def find_runner_by_name(pd, name):
    """Find a runner by name."""
    try:
        runners = pd.client.list_all(API_PATH, LIST_KEY)
    except PagerDutyError:
        return None
    for runner in runners:
        if runner.get('name') == name:
            return runner
    return None


def build_payload(module):
    """Build the runner payload."""
    data = {
        'name': module.params['name'],
        'description': module.params['description'],
        'runner_type': module.params['runner_type'],
    }
    if module.params['teams']:
        data['teams'] = [{'id': t, 'type': 'team_reference'} for t in module.params['teams']]
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
        runner_type=dict(type='str', required=True, choices=['sidecar', 'runbook']),
        teams=dict(type='list', elements='str', default=[]),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        existing = find_runner_by_name(pd, module.params['name'])

        if state == 'present':
            payload = build_payload(module)
            if existing:
                if not pd.check_mode:
                    result = pd.client.put(
                        '{0}/{1}'.format(API_PATH, existing['id']),
                        {RESOURCE_KEY: payload},
                    )
                    pd.result[RESOURCE_KEY] = result.get(RESOURCE_KEY, result)
                else:
                    pd.result[RESOURCE_KEY] = existing
                pd.result['changed'] = True
            else:
                if not pd.check_mode:
                    result = pd.client.post(API_PATH, {RESOURCE_KEY: payload})
                    pd.result[RESOURCE_KEY] = result.get(RESOURCE_KEY, result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete('{0}/{1}'.format(API_PATH, existing['id']))
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
