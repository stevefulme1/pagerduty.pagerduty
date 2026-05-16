#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: user_contact_method
short_description: Manage PagerDuty user contact methods
description:
  - Create, update, or delete contact methods for a PagerDuty user.
version_added: "1.0.0"
author: Ansible Ansible PagerDuty Collection Authors (@ansible-collections) (@ansible-collections)
options:
  user:
    description: The user name, email, or ID.
    type: str
    required: true
  type:
    description: The contact method type.
    type: str
    required: true
    choices:
      - email_contact_method
      - phone_contact_method
      - push_notification_contact_method
      - sms_contact_method
  address:
    description: The address or phone number for the contact method.
    type: str
    required: true
  label:
    description: A label for the contact method.
    type: str
    required: true
  country_code:
    description: Country code for phone/SMS contact methods.
    type: int
  state:
    description: Whether the contact method should exist.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Add an email contact method
  pagerduty.pagerduty.user_contact_method:
    user: jane.doe@example.com
    type: email_contact_method
    address: jane.doe@example.com
    label: Work Email
    api_token: "{{ pagerduty_token }}"

- name: Add a phone contact method
  pagerduty.pagerduty.user_contact_method:
    user: PUSER123
    type: phone_contact_method
    address: "5551234567"
    label: Mobile
    country_code: 1
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
contact_method:
  description: The contact method object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_user_id(pd, user_param):
    if user_param.startswith('P') and len(user_param) >= 7:
        return user_param
    params = {'query': user_param}
    users = pd.client.list_all('/users', 'users', params=params)
    for u in users:
        if u.get('email') == user_param or u.get('name') == user_param:
            return u['id']
    pd.fail('User not found: {0}'.format(user_param))


def find_contact_method(pd, user_id, cm_type, address):
    methods = pd.client.list_all('/users/{0}/contact_methods'.format(user_id), 'contact_methods')
    for m in methods:
        if m.get('type') == cm_type and m.get('address') == address:
            return m
    return None


def main():
    argument_spec = dict(
        user=dict(type='str', required=True),
        type=dict(type='str', required=True, choices=[
            'email_contact_method', 'phone_contact_method',
            'push_notification_contact_method', 'sms_contact_method',
        ]),
        address=dict(type='str', required=True),
        label=dict(type='str', required=True),
        country_code=dict(type='int'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        user_id = resolve_user_id(pd, module.params['user'])
        cm_type = module.params['type']
        address = module.params['address']
        existing = find_contact_method(pd, user_id, cm_type, address)
        base_path = '/users/{0}/contact_methods'.format(user_id)

        if module.params['state'] == 'present':
            data = {
                'type': cm_type,
                'address': address,
                'label': module.params['label'],
            }
            if module.params.get('country_code') is not None:
                data['country_code'] = module.params['country_code']

            if existing:
                changes = pd._diff(existing, data, ['label', 'address', 'country_code'])
                if changes:
                    if not pd.check_mode:
                        result = pd.client.put(
                            '{0}/{1}'.format(base_path, existing['id']),
                            {'contact_method': changes},
                        )
                        pd.result['contact_method'] = result.get('contact_method', result)
                    else:
                        pd.result['contact_method'] = existing
                    pd.result['changed'] = True
                else:
                    pd.result['contact_method'] = existing
            else:
                if not pd.check_mode:
                    result = pd.client.post(base_path, {'contact_method': data})
                    pd.result['contact_method'] = result.get('contact_method', result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete('{0}/{1}'.format(base_path, existing['id']))
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
