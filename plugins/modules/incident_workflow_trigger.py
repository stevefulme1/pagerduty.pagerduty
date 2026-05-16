#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incident_workflow_trigger
short_description: Manage PagerDuty incident workflow triggers
description:
  - Create, update, and delete triggers for incident workflows.
  - Triggers determine when a workflow is automatically invoked.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  workflow:
    description: The name or ID of the incident workflow to trigger.
    type: str
    required: true
  type:
    description: The trigger type.
    type: str
    required: true
    choices: [manual, conditional]
  condition:
    description: The trigger condition expression (required for conditional triggers).
    type: str
  subscribed_to_all_services:
    description: Whether the trigger applies to all services.
    type: bool
    default: false
  services:
    description: List of service IDs the trigger is scoped to.
    type: list
    elements: str
    default: []
  state:
    description: Whether the trigger should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a conditional workflow trigger
  pagerduty.pagerduty.incident_workflow_trigger:
    api_token: "{{ pd_token }}"
    workflow: "SEV1 Response"
    type: conditional
    condition: "incident.priority.name matches 'P1'"
    subscribed_to_all_services: false
    services:
      - PXXXXXX
    state: present

- name: Create a manual workflow trigger
  pagerduty.pagerduty.incident_workflow_trigger:
    api_token: "{{ pd_token }}"
    workflow: "PWFXXXX"
    type: manual
    subscribed_to_all_services: true
    state: present

- name: Delete a workflow trigger
  pagerduty.pagerduty.incident_workflow_trigger:
    api_token: "{{ pd_token }}"
    workflow: "SEV1 Response"
    type: manual
    state: absent
'''

RETURN = r'''
trigger:
  description: The workflow trigger object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_workflow(pd, workflow_input):
    """Resolve a workflow name or ID to its ID."""
    existing = pd.client.find_by_id('/incident_workflows/{0}'.format(workflow_input), 'incident_workflow')
    if existing:
        return existing['id']
    found = pd.client.find_by_name('/incident_workflows', 'incident_workflows', workflow_input)
    if found:
        return found['id']
    return None


def find_trigger(pd, workflow_id, trigger_type):
    """Find a trigger by workflow ID and type."""
    path = '/incident_workflows/{0}/triggers'.format(workflow_id)
    try:
        triggers = pd.client.list_all(path, 'triggers')
    except PagerDutyError:
        return None
    for trigger in triggers:
        if trigger.get('type', '').replace('_trigger', '') == trigger_type:
            return trigger
    return None


def build_payload(module, workflow_id):
    """Build the trigger payload."""
    data = {
        'type': '{0}_trigger'.format(module.params['type']),
        'workflow': {'id': workflow_id, 'type': 'workflow_reference'},
        'subscribed_to_all_services': module.params['subscribed_to_all_services'],
    }
    if module.params['condition']:
        data['condition'] = module.params['condition']
    if module.params['services']:
        data['services'] = [{'id': s, 'type': 'service_reference'} for s in module.params['services']]
    return data


def main():
    argument_spec = dict(
        workflow=dict(type='str', required=True),
        type=dict(type='str', required=True, choices=['manual', 'conditional']),
        condition=dict(type='str'),
        subscribed_to_all_services=dict(type='bool', default=False),
        services=dict(type='list', elements='str', default=[]),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        workflow_id = resolve_workflow(pd, module.params['workflow'])
        if not workflow_id:
            pd.fail('Workflow not found: {0}'.format(module.params['workflow']))

        existing = find_trigger(pd, workflow_id, module.params['type'])
        trigger_path = '/incident_workflows/{0}/triggers'.format(workflow_id)

        if state == 'present':
            payload = build_payload(module, workflow_id)
            if existing:
                if not pd.check_mode:
                    result = pd.client.put(
                        '{0}/{1}'.format(trigger_path, existing['id']),
                        {'trigger': payload},
                    )
                    pd.result['trigger'] = result.get('trigger', result)
                else:
                    pd.result['trigger'] = existing
                pd.result['changed'] = True
            else:
                if not pd.check_mode:
                    result = pd.client.post(trigger_path, {'trigger': payload})
                    pd.result['trigger'] = result.get('trigger', result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete('{0}/{1}'.format(trigger_path, existing['id']))
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
