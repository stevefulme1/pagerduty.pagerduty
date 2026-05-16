#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: team_info
short_description: List or get PagerDuty teams
description:
  - Retrieve a single team by ID or name, or list all teams.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific team to retrieve.
    type: str
  name:
    description: Filter teams by exact name match.
    type: str
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get a specific team
  pagerduty.pagerduty.team_info:
    id: PTEAM01
  register: result

- name: Find a team by name
  pagerduty.pagerduty.team_info:
    name: Platform Engineering
  register: result

- name: List all teams
  pagerduty.pagerduty.team_info:
  register: result
'''

RETURN = r'''
teams:
  description: List of teams matching the query.
  type: list
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyClient, PagerDutyError,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            id=dict(type='str'),
            name=dict(type='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        if params['id']:
            team = client.get('/teams/{0}'.format(params['id']))
            module.exit_json(changed=False, teams=[team.get('team', team)])
        else:
            qp = {}
            if params['name']:
                qp['query'] = params['name']
            teams = client.list_all('/teams', 'teams', params=qp or None)
            if params['name']:
                teams = [t for t in teams if t.get('name') == params['name']]
            module.exit_json(changed=False, teams=teams)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
