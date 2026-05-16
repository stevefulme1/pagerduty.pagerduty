#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: team
short_description: Manage PagerDuty teams
description:
  - Create, update, or delete PagerDuty teams.
version_added: "1.0.0"
author: PagerDuty Collection Authors
options:
  name:
    description: The name of the team.
    type: str
    required: true
  description:
    description: A description of the team.
    type: str
  parent:
    description: The parent team name or ID for nested teams.
    type: str
  state:
    description: Whether the team should exist.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a team
  pagerduty.pagerduty.team:
    name: Engineering
    description: Engineering team
    api_token: "{{ pagerduty_token }}"

- name: Create a sub-team
  pagerduty.pagerduty.team:
    name: Backend Engineering
    description: Backend sub-team
    parent: Engineering
    api_token: "{{ pagerduty_token }}"

- name: Delete a team
  pagerduty.pagerduty.team:
    name: Engineering
    state: absent
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
team:
  description: The team object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_parent(pd, parent_param):
    if not parent_param:
        return None
    if parent_param.startswith('P') and len(parent_param) >= 7:
        return {'id': parent_param, 'type': 'team_reference'}
    team = pd.client.find_by_name('/teams', 'teams', parent_param)
    if not team:
        pd.fail('Parent team not found: {0}'.format(parent_param))
    return {'id': team['id'], 'type': 'team_reference'}


def build_team_data(pd):
    params = pd.module.params
    data = {'name': params['name'], 'type': 'team'}
    if params.get('description') is not None:
        data['description'] = params['description']
    parent = resolve_parent(pd, params.get('parent'))
    if parent:
        data['parent'] = parent
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str'),
        parent=dict(type='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        if module.params['state'] == 'present':
            pd.ensure_present(
                resource_key='team',
                find_path='/teams',
                find_key='teams',
                create_path='/teams',
                create_data=build_team_data(pd),
                update_path_tmpl='/teams/{id}',
                update_data_fn=lambda: build_team_data(pd),
                compare_keys=['name', 'description', 'parent'],
            )
        else:
            pd.ensure_absent(
                resource_key='team',
                find_path='/teams',
                find_key='teams',
                delete_path_tmpl='/teams/{id}',
            )
        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
