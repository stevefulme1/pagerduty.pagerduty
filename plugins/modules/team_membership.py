#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: team_membership
short_description: Manage PagerDuty team membership
description:
  - Add or remove users from PagerDuty teams.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  team:
    description: The team name or ID.
    type: str
    required: true
  user:
    description: The user name, email, or ID.
    type: str
    required: true
  role:
    description: The user's role on the team.
    type: str
    choices: [manager, observer, responder]
    default: responder
  state:
    description: Whether the user should be a member of the team.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Add a user to a team
  pagerduty.pagerduty.team_membership:
    team: Engineering
    user: jane.doe@example.com
    role: responder
    api_token: "{{ pagerduty_token }}"

- name: Remove a user from a team
  pagerduty.pagerduty.team_membership:
    team: Engineering
    user: jane.doe@example.com
    state: absent
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
membership:
  description: The membership details.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_team_id(pd, team_param):
    if team_param.startswith('P') and len(team_param) >= 7:
        return team_param
    team = pd.client.find_by_name('/teams', 'teams', team_param)
    if not team:
        pd.fail('Team not found: {0}'.format(team_param))
    return team['id']


def resolve_user_id(pd, user_param):
    if user_param.startswith('P') and len(user_param) >= 7:
        return user_param
    params = {'query': user_param}
    users = pd.client.list_all('/users', 'users', params=params)
    for u in users:
        if u.get('email') == user_param or u.get('name') == user_param:
            return u['id']
    pd.fail('User not found: {0}'.format(user_param))


def get_membership(pd, team_id, user_id):
    try:
        members = pd.client.list_all('/teams/{0}/members'.format(team_id), 'members')
        for m in members:
            if m.get('user', {}).get('id') == user_id:
                return m
    except PagerDutyError:
        pass
    return None


def main():
    argument_spec = dict(
        team=dict(type='str', required=True),
        user=dict(type='str', required=True),
        role=dict(type='str', choices=['manager', 'observer', 'responder'], default='responder'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        team_id = resolve_team_id(pd, module.params['team'])
        user_id = resolve_user_id(pd, module.params['user'])
        role = module.params['role']
        path = '/teams/{0}/users/{1}'.format(team_id, user_id)

        existing = get_membership(pd, team_id, user_id)

        if module.params['state'] == 'present':
            if existing:
                current_role = existing.get('role', 'responder')
                if current_role != role:
                    if not pd.check_mode:
                        pd.client.put(path, {'role': role})
                    pd.result['changed'] = True
                pd.result['membership'] = {'team_id': team_id, 'user_id': user_id, 'role': role}
            else:
                if not pd.check_mode:
                    pd.client.put(path, {'role': role})
                pd.result['changed'] = True
                pd.result['membership'] = {'team_id': team_id, 'user_id': user_id, 'role': role}
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete(path)
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
