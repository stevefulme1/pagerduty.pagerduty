#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incident
short_description: Manage PagerDuty incidents
description:
  - Create, update, and resolve PagerDuty incidents.
  - For updates, the C(id) parameter is required.
version_added: "1.0.0"
author: "Ansible PagerDuty Collection Authors (@ansible-collections)"
options:
  id:
    description: Incident ID for updates.
    type: str
  title:
    description: Incident title. Required when creating.
    type: str
  service:
    description: Service name or ID to associate with the incident.
    type: str
  urgency:
    description: Incident urgency.
    type: str
    choices: [high, low]
  body:
    description: Incident body details.
    type: str
  escalation_policy:
    description: Escalation policy name or ID.
    type: str
  priority:
    description: Priority name or ID.
    type: str
  incident_key:
    description: Deduplication key for the incident.
    type: str
  status:
    description: Incident status.
    type: str
    choices: [triggered, acknowledged, resolved]
  assignments:
    description: List of user IDs to assign.
    type: list
    elements: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create an incident
  pagerduty.pagerduty.incident:
    api_token: "{{ pd_token }}"
    title: "Server outage"
    service: "Web Application"
    urgency: high
    state: present

- name: Resolve an incident
  pagerduty.pagerduty.incident:
    api_token: "{{ pd_token }}"
    id: "P1234567"
    status: resolved
    state: present
'''

RETURN = r'''
incident:
  description: The incident object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_ref(client, value, path, resource_key):
    """Resolve a name or ID to an API reference dict."""
    if not value:
        return None
    # If it looks like an ID, use it directly
    if value.startswith('P') and len(value) >= 7:
        return {'id': value, 'type': resource_key + '_reference'}
    found = client.find_by_name(path, resource_key + 's', value)
    if not found:
        raise PagerDutyError('Could not find {0} named "{1}"'.format(resource_key, value))
    return {'id': found['id'], 'type': resource_key + '_reference'}


def build_incident_data(client, params):
    data = {}
    if params.get('title'):
        data['title'] = params['title']
    if params.get('urgency'):
        data['urgency'] = params['urgency']
    if params.get('incident_key'):
        data['incident_key'] = params['incident_key']
    if params.get('status'):
        data['status'] = params['status']
    if params.get('body'):
        data['body'] = {'type': 'incident_body', 'details': params['body']}

    service_ref = resolve_ref(client, params.get('service'), '/services', 'service')
    if service_ref:
        data['service'] = service_ref

    ep_ref = resolve_ref(client, params.get('escalation_policy'), '/escalation_policies', 'escalation_policy')
    if ep_ref:
        data['escalation_policy'] = ep_ref

    if params.get('priority'):
        pri = params['priority']
        priorities = client.list_all('/priorities', 'priorities')
        match = next((p for p in priorities if p['id'] == pri or p['name'] == pri), None)
        if not match:
            raise PagerDutyError('Could not find priority "{0}"'.format(pri))
        data['priority'] = {'id': match['id'], 'type': 'priority_reference'}

    if params.get('assignments'):
        data['assignments'] = [
            {'assignee': {'id': uid, 'type': 'user_reference'}} for uid in params['assignments']
        ]

    data['type'] = 'incident'
    return data


def main():
    argument_spec = dict(
        id=dict(type='str'),
        title=dict(type='str'),
        service=dict(type='str'),
        urgency=dict(type='str', choices=['high', 'low']),
        body=dict(type='str'),
        escalation_policy=dict(type='str'),
        priority=dict(type='str'),
        incident_key=dict(type='str', no_log=False),
        status=dict(type='str', choices=['triggered', 'acknowledged', 'resolved']),
        assignments=dict(type='list', elements='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ('title', 'id'), True),
        ],
    )

    pd = PagerDutyModule(module)

    try:
        state = module.params['state']
        incident_id = module.params.get('id')

        if state == 'absent':
            if not incident_id:
                pd.fail('id is required to resolve/remove an incident')
            existing = pd.client.find_by_id('/incidents/{0}'.format(incident_id), 'incident')
            if existing and existing.get('status') != 'resolved':
                if not pd.check_mode:
                    pd.client.put('/incidents/{0}'.format(incident_id),
                                  {'incident': {'type': 'incident', 'status': 'resolved'}})
                pd.result['changed'] = True
        else:
            data = build_incident_data(pd.client, module.params)
            if incident_id:
                existing = pd.client.find_by_id('/incidents/{0}'.format(incident_id), 'incident')
                if existing:
                    if not pd.check_mode:
                        result = pd.client.put('/incidents/{0}'.format(incident_id), {'incident': data})
                        pd.result['incident'] = result.get('incident', result)
                    pd.result['changed'] = True
                else:
                    pd.fail('Incident {0} not found'.format(incident_id))
            else:
                if not module.params.get('service'):
                    pd.fail('service is required when creating an incident')
                if not pd.check_mode:
                    result = pd.client.post('/incidents', {'incident': data})
                    pd.result['incident'] = result.get('incident', result)
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
