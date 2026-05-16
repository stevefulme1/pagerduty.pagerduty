#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: business_service
short_description: Manage PagerDuty business services
description:
  - Create, update, and delete PagerDuty business services.
  - Business services represent high-level business capabilities.
version_added: "1.0.0"
author: "PagerDuty Collection Authors"
options:
  id:
    description: Business service ID for updates or deletion.
    type: str
  name:
    description: Name of the business service.
    type: str
  description:
    description: Description of the business service.
    type: str
  point_of_contact:
    description: Point of contact for the business service.
    type: str
  team:
    description: Team name or ID to associate with the business service.
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
- name: Create a business service
  pagerduty.pagerduty.business_service:
    api_token: "{{ pd_token }}"
    name: "E-Commerce Platform"
    description: "Customer-facing shopping experience"
    point_of_contact: "platform-team@example.com"
    team: "Platform Team"
    state: present

- name: Delete a business service
  pagerduty.pagerduty.business_service:
    api_token: "{{ pd_token }}"
    name: "Legacy Service"
    state: absent
'''

RETURN = r'''
business_service:
  description: The business service object.
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
        point_of_contact=dict(type='str'),
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
    path = '/business_services'
    resource_key = 'business_service'

    try:
        if params['state'] == 'absent':
            pd.ensure_absent(resource_key, path, 'business_services', path + '/{id}', id_field='id')
        else:
            create_data = {'name': params['name'], 'type': 'business_service'}
            if params.get('description'):
                create_data['description'] = params['description']
            if params.get('point_of_contact'):
                create_data['point_of_contact'] = params['point_of_contact']

            team_ref = resolve_team(pd.client, params.get('team'))
            if team_ref:
                create_data['team'] = team_ref

            def update_data():
                return dict(create_data)

            pd.ensure_present(
                resource_key=resource_key,
                find_path=path,
                find_key='business_services',
                create_path=path,
                create_data=create_data,
                update_path_tmpl=path + '/{id}',
                update_data_fn=update_data,
                compare_keys=['name', 'description', 'point_of_contact', 'team'],
                id_field='id',
            )

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
