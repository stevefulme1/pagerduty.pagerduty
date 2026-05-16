#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event_orchestration_integration
short_description: Manage PagerDuty event orchestration integrations
description:
  - Create, update, and delete integrations for event orchestrations.
  - Each integration provides a unique routing key for sending events.
version_added: "1.0.0"
author: "PagerDuty Collection Authors"
options:
  id:
    description: Integration ID for updates or deletion.
    type: str
  orchestration:
    description: Event orchestration name or ID.
    type: str
    required: true
  label:
    description: Label for the integration.
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create an orchestration integration
  pagerduty.pagerduty.event_orchestration_integration:
    api_token: "{{ pd_token }}"
    orchestration: "Production Orchestration"
    label: "Ansible Integration"
    state: present

- name: Delete an orchestration integration
  pagerduty.pagerduty.event_orchestration_integration:
    api_token: "{{ pd_token }}"
    orchestration: "Production Orchestration"
    id: "P1234567"
    state: absent
'''

RETURN = r'''
integration:
  description: The integration object.
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


def find_integration_by_label(client, orch_id, label):
    path = '/event_orchestrations/{0}/integrations'.format(orch_id)
    result = client.get(path)
    integrations = result.get('integrations', [])
    for i in integrations:
        if i.get('label') == label:
            return i
    return None


def main():
    argument_spec = dict(
        id=dict(type='str'),
        orchestration=dict(type='str', required=True),
        label=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ('label',)),
            ('state', 'absent', ('label', 'id'), True),
        ],
    )

    pd = PagerDutyModule(module)
    params = module.params

    try:
        orch_id = resolve_orchestration(pd.client, params['orchestration'])
        base_path = '/event_orchestrations/{0}/integrations'.format(orch_id)
        integration_id = params.get('id')
        label = params.get('label')

        if params['state'] == 'absent':
            existing = None
            if integration_id:
                existing = pd.client.find_by_id('{0}/{1}'.format(base_path, integration_id))
            elif label:
                existing = find_integration_by_label(pd.client, orch_id, label)

            if existing:
                if not pd.check_mode:
                    pd.client.delete('{0}/{1}'.format(base_path, existing['id']))
                pd.result['changed'] = True
        else:
            existing = None
            if integration_id:
                existing = pd.client.find_by_id('{0}/{1}'.format(base_path, integration_id))
            elif label:
                existing = find_integration_by_label(pd.client, orch_id, label)

            if existing:
                if existing.get('label') != label:
                    if not pd.check_mode:
                        result = pd.client.put(
                            '{0}/{1}'.format(base_path, existing['id']),
                            {'integration': {'label': label}}
                        )
                        pd.result['integration'] = result.get('integration', result)
                    pd.result['changed'] = True
                else:
                    pd.result['integration'] = existing
            else:
                if not pd.check_mode:
                    result = pd.client.post(base_path, {'integration': {'label': label}})
                    pd.result['integration'] = result.get('integration', result)
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
