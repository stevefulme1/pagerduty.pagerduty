#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incident_workflow
short_description: Manage PagerDuty incident workflows
description:
  - Create, update, and delete incident workflows in PagerDuty.
  - Incident workflows automate actions during incident response.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  name:
    description: The name of the incident workflow.
    type: str
    required: true
  description:
    description: A description of the workflow.
    type: str
    default: ''
  team:
    description: The team name or ID that owns the workflow.
    type: str
  steps:
    description:
      - List of workflow steps.
      - Each step is a dict with name and action_configuration.
    type: list
    elements: dict
    default: []
  state:
    description: Whether the workflow should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create an incident workflow
  pagerduty.pagerduty.incident_workflow:
    api_token: "{{ pd_token }}"
    name: "SEV1 Response"
    description: "Automated SEV1 incident handling"
    steps:
      - name: "Add responders"
        action_configuration:
          action_id: "add_responders"
          inputs:
            responders:
              - type: escalation_policy_reference
                id: PXXXXXX
    state: present

- name: Delete an incident workflow
  pagerduty.pagerduty.incident_workflow:
    api_token: "{{ pd_token }}"
    name: "Old Workflow"
    state: absent
'''

RETURN = r'''
incident_workflow:
  description: The incident workflow object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)

API_PATH = '/incident_workflows'
RESOURCE_KEY = 'incident_workflow'
LIST_KEY = 'incident_workflows'


def resolve_team(pd, team_input):
    """Resolve a team name or ID to a team reference."""
    if not team_input:
        return None
    team = pd.client.find_by_id('/teams/{0}'.format(team_input), 'team')
    if team:
        return {'id': team['id'], 'type': 'team_reference'}
    team = pd.client.find_by_name('/teams', 'teams', team_input)
    if team:
        return {'id': team['id'], 'type': 'team_reference'}
    return None


def build_payload(module, pd):
    """Build the incident workflow payload."""
    data = {
        'name': module.params['name'],
        'description': module.params['description'],
    }
    if module.params['team']:
        team_ref = resolve_team(pd, module.params['team'])
        if team_ref:
            data['team'] = team_ref
    if module.params['steps']:
        data['steps'] = module.params['steps']
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
        team=dict(type='str'),
        steps=dict(type='list', elements='dict', default=[]),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        existing = pd.client.find_by_name(API_PATH, LIST_KEY, module.params['name'])

        if state == 'present':
            payload = build_payload(module, pd)
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
