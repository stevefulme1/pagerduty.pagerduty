#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: user_info
short_description: List or get PagerDuty users
description:
  - Retrieve a single user by ID, name, or email, or list all users with optional filters.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific user to retrieve.
    type: str
  name:
    description: Filter users by exact name match.
    type: str
  email:
    description: Filter users by exact email match.
    type: str
  team_ids:
    description: List of team IDs to filter users by.
    type: list
    elements: str
  include:
    description: Additional data to include in the response.
    type: list
    elements: str
    choices: [contact_methods, notification_rules]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get a specific user
  pagerduty.pagerduty.user_info:
    id: PUSER01
  register: result

- name: Find a user by email
  pagerduty.pagerduty.user_info:
    email: oncall@example.com
  register: result

- name: List users on a team with contact methods
  pagerduty.pagerduty.user_info:
    team_ids: ["PTEAM01"]
    include: [contact_methods]
  register: result
'''

RETURN = r'''
users:
  description: List of users matching the query.
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
            email=dict(type='str'),
            team_ids=dict(type='list', elements='str'),
            include=dict(type='list', elements='str', choices=['contact_methods', 'notification_rules']),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        if params['id']:
            qp = {}
            if params['include']:
                qp['include[]'] = ','.join(params['include'])
            user = client.get('/users/{0}'.format(params['id']), params=qp or None)
            module.exit_json(changed=False, users=[user.get('user', user)])
        else:
            qp = {}
            if params['name']:
                qp['query'] = params['name']
            elif params['email']:
                qp['query'] = params['email']
            if params['team_ids']:
                qp['team_ids[]'] = ','.join(params['team_ids'])
            if params['include']:
                qp['include[]'] = ','.join(params['include'])
            users = client.list_all('/users', 'users', params=qp or None)
            if params['name']:
                users = [u for u in users if u.get('name') == params['name']]
            if params['email']:
                users = [u for u in users if u.get('email') == params['email']]
            module.exit_json(changed=False, users=users)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
