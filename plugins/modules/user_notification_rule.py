#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: user_notification_rule
short_description: Manage PagerDuty user notification rules
description:
  - Create, update, or delete notification rules for a PagerDuty user.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  user:
    description: The user name, email, or ID.
    type: str
    required: true
  type:
    description: The notification rule type.
    type: str
    default: assignment_notification_rule
  start_delay_in_minutes:
    description: Minutes to wait before sending the notification.
    type: int
    required: true
  urgency:
    description: The urgency of incidents that trigger this rule.
    type: str
    required: true
    choices: [high, low]
  contact_method:
    description: >
      The contact method for the notification rule.
      Dict with type and id keys.
    type: dict
    required: true
  state:
    description: Whether the notification rule should exist.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a notification rule
  pagerduty.pagerduty.user_notification_rule:
    user: jane.doe@example.com
    start_delay_in_minutes: 0
    urgency: high
    contact_method:
      type: email_contact_method_reference
      id: PCMETH01
    api_token: "{{ pagerduty_token }}"

- name: Delete a notification rule
  pagerduty.pagerduty.user_notification_rule:
    user: jane.doe@example.com
    start_delay_in_minutes: 0
    urgency: high
    contact_method:
      type: email_contact_method_reference
      id: PCMETH01
    state: absent
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
notification_rule:
  description: The notification rule object.
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


def find_matching_rule(pd, user_id, urgency, delay, contact_method_id):
    rules = pd.client.list_all('/users/{0}/notification_rules'.format(user_id), 'notification_rules')
    for r in rules:
        if (r.get('urgency') == urgency
                and r.get('start_delay_in_minutes') == delay
                and r.get('contact_method', {}).get('id') == contact_method_id):
            return r
    return None


def main():
    argument_spec = dict(
        user=dict(type='str', required=True),
        type=dict(type='str', default='assignment_notification_rule'),
        start_delay_in_minutes=dict(type='int', required=True),
        urgency=dict(type='str', required=True, choices=['high', 'low']),
        contact_method=dict(type='dict', required=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        user_id = resolve_user_id(pd, module.params['user'])
        urgency = module.params['urgency']
        delay = module.params['start_delay_in_minutes']
        contact_method = module.params['contact_method']
        base_path = '/users/{0}/notification_rules'.format(user_id)

        existing = find_matching_rule(pd, user_id, urgency, delay, contact_method.get('id'))

        if module.params['state'] == 'present':
            data = {
                'type': module.params['type'],
                'start_delay_in_minutes': delay,
                'urgency': urgency,
                'contact_method': contact_method,
            }
            if not existing:
                if not pd.check_mode:
                    result = pd.client.post(base_path, {'notification_rule': data})
                    pd.result['notification_rule'] = result.get('notification_rule', result)
                pd.result['changed'] = True
            else:
                changes = pd._diff(existing, data, ['start_delay_in_minutes', 'urgency', 'contact_method'])
                if changes:
                    if not pd.check_mode:
                        result = pd.client.put(
                            '{0}/{1}'.format(base_path, existing['id']),
                            {'notification_rule': changes},
                        )
                        pd.result['notification_rule'] = result.get('notification_rule', result)
                    else:
                        pd.result['notification_rule'] = existing
                    pd.result['changed'] = True
                else:
                    pd.result['notification_rule'] = existing
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
