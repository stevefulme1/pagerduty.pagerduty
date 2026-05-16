#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: user
short_description: Manage PagerDuty users
description:
  - Create, update, or delete PagerDuty users.
version_added: "1.0.0"
author: PagerDuty Collection Authors
options:
  name:
    description: The name of the user.
    type: str
    required: true
  email:
    description: The user's email address. Used as the unique identifier.
    type: str
    required: true
  role:
    description: The user's role.
    type: str
    choices: [admin, limited_user, observer, owner, read_only_limited_user, read_only_user, restricted_access, user]
  time_zone:
    description: The user's time zone.
    type: str
  color:
    description: The user's schedule color.
    type: str
  description:
    description: A description of the user.
    type: str
  job_title:
    description: The user's job title.
    type: str
  state:
    description: Whether the user should exist.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a user
  pagerduty.pagerduty.user:
    name: Jane Doe
    email: jane.doe@example.com
    role: user
    time_zone: America/New_York
    api_token: "{{ pagerduty_token }}"

- name: Delete a user
  pagerduty.pagerduty.user:
    name: Jane Doe
    email: jane.doe@example.com
    state: absent
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
user:
  description: The user object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def find_user_by_email(pd, email):
    params = {'query': email}
    users = pd.client.list_all('/users', 'users', params=params)
    for u in users:
        if u.get('email') == email:
            return u
    return None


def build_user_data(module):
    data = {
        'name': module.params['name'],
        'email': module.params['email'],
        'type': 'user',
    }
    for key in ('role', 'time_zone', 'color', 'description', 'job_title'):
        if module.params.get(key) is not None:
            data[key] = module.params[key]
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        email=dict(type='str', required=True),
        role=dict(type='str', choices=[
            'admin', 'limited_user', 'observer', 'owner',
            'read_only_limited_user', 'read_only_user', 'restricted_access', 'user',
        ]),
        time_zone=dict(type='str'),
        color=dict(type='str'),
        description=dict(type='str'),
        job_title=dict(type='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        existing = find_user_by_email(pd, module.params['email'])

        if module.params['state'] == 'present':
            desired = build_user_data(module)
            if existing:
                compare_keys = ['name', 'email', 'role', 'time_zone', 'color', 'description', 'job_title']
                changes = pd._diff(existing, desired, compare_keys)
                if changes:
                    if not pd.check_mode:
                        result = pd.client.put('/users/{0}'.format(existing['id']), {'user': changes})
                        pd.result['user'] = result.get('user', result)
                    else:
                        pd.result['user'] = existing
                    pd.result['changed'] = True
                else:
                    pd.result['user'] = existing
            else:
                if not pd.check_mode:
                    result = pd.client.post('/users', {'user': desired})
                    pd.result['user'] = result.get('user', result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete('/users/{0}'.format(existing['id']))
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
