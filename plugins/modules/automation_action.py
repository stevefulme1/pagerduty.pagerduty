#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: automation_action
short_description: Manage PagerDuty automation actions
description:
  - Create, update, and delete automation actions in PagerDuty.
  - Automation actions run Process Automation jobs or scripts in response to incidents.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  name:
    description: The name of the automation action.
    type: str
    required: true
  description:
    description: A description of the automation action.
    type: str
    default: ''
  action_type:
    description: The type of automation action.
    type: str
    required: true
    choices: [process_automation, script]
  action_data_reference:
    description:
      - A dict describing the action to run.
      - For process_automation, include process_automation_job_id.
      - For script, include script (the script body).
    type: dict
    required: true
  services:
    description: List of service IDs this action is associated with.
    type: list
    elements: str
    default: []
  teams:
    description: List of team IDs this action is associated with.
    type: list
    elements: str
    default: []
  runner:
    description: The runner ID to execute this action.
    type: str
  state:
    description: Whether the automation action should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a Process Automation action
  pagerduty.pagerduty.automation_action:
    api_token: "{{ pd_token }}"
    name: "Restart Service"
    description: "Restart the application service"
    action_type: process_automation
    action_data_reference:
      process_automation_job_id: "job-uuid-here"
    runner: PRUNNER1
    services:
      - PXXXXXX
    state: present

- name: Create a script action
  pagerduty.pagerduty.automation_action:
    api_token: "{{ pd_token }}"
    name: "Diagnostic Script"
    description: "Run diagnostics on the host"
    action_type: script
    action_data_reference:
      script: "#!/bin/bash\necho 'Running diagnostics...'"
    runner: PRUNNER1
    state: present

- name: Delete an automation action
  pagerduty.pagerduty.automation_action:
    api_token: "{{ pd_token }}"
    name: "Old Action"
    action_type: script
    action_data_reference: {}
    state: absent
'''

RETURN = r'''
action:
  description: The automation action object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)

API_PATH = '/automation_actions/actions'
RESOURCE_KEY = 'action'
LIST_KEY = 'actions'


def find_action_by_name(pd, name):
    """Find an automation action by name."""
    try:
        actions = pd.client.list_all(API_PATH, LIST_KEY)
    except PagerDutyError:
        return None
    for action in actions:
        if action.get('name') == name:
            return action
    return None


def build_payload(module):
    """Build the automation action payload."""
    data = {
        'name': module.params['name'],
        'description': module.params['description'],
        'action_type': module.params['action_type'],
        'action_data_reference': module.params['action_data_reference'],
    }
    if module.params['runner']:
        data['runner'] = module.params['runner']
    if module.params['services']:
        data['services'] = [{'id': s, 'type': 'service_reference'} for s in module.params['services']]
    if module.params['teams']:
        data['teams'] = [{'id': t, 'type': 'team_reference'} for t in module.params['teams']]
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
        action_type=dict(type='str', required=True, choices=['process_automation', 'script']),
        action_data_reference=dict(type='dict', required=True),
        services=dict(type='list', elements='str', default=[]),
        teams=dict(type='list', elements='str', default=[]),
        runner=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        existing = find_action_by_name(pd, module.params['name'])

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
