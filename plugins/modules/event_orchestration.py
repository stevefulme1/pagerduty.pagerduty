#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event_orchestration
short_description: Manage PagerDuty event orchestrations
description:
  - Create, update, and delete PagerDuty event orchestrations.
version_added: "1.0.0"
author: "PagerDuty Collection Authors"
options:
  id:
    description: Orchestration ID for updates or deletion.
    type: str
  name:
    description: Name of the event orchestration.
    type: str
  description:
    description: Description of the event orchestration.
    type: str
  team:
    description: Team name or ID to associate with the orchestration.
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
- name: Create an event orchestration
  pagerduty.pagerduty.event_orchestration:
    api_token: "{{ pd_token }}"
    name: "Production Orchestration"
    description: "Routes production events"
    team: "Platform Team"
    state: present

- name: Delete an event orchestration
  pagerduty.pagerduty.event_orchestration:
    api_token: "{{ pd_token }}"
    name: "Old Orchestration"
    state: absent
'''

RETURN = r'''
orchestration:
  description: The orchestration object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_team(client, team):
    if not team:
        return None
    if team.startswith('P') and len(team) >= 7:
        return {'id': team, 'type': 'team_reference'}
    found = client.find_by_name('/teams', 'teams', team)
    if not found:
        raise PagerDutyError('Could not find team "{0}"'.format(team))
    return {'id': found['id'], 'type': 'team_reference'}


def main():
    argument_spec = dict(
        id=dict(type='str'),
        name=dict(type='str'),
        description=dict(type='str'),
        team=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ('name',)),
            ('state', 'absent', ('name', 'id'), True),
        ],
    )

    pd = PagerDutyModule(module)
    params = module.params
    path = '/event_orchestrations'
    resource_key = 'orchestration'

    try:
        if params['state'] == 'absent':
            pd.ensure_absent(resource_key, path, 'orchestrations', path + '/{id}', id_field='id')
        else:
            create_data = {'name': params['name']}
            if params.get('description'):
                create_data['description'] = params['description']

            team_ref = resolve_team(pd.client, params.get('team'))
            if team_ref:
                create_data['team'] = team_ref

            def update_data():
                data = dict(create_data)
                return data

            pd.ensure_present(
                resource_key=resource_key,
                find_path=path,
                find_key='orchestrations',
                create_path=path,
                create_data=create_data,
                update_path_tmpl=path + '/{id}',
                update_data_fn=update_data,
                compare_keys=['name', 'description', 'team'],
                id_field='id',
            )

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
