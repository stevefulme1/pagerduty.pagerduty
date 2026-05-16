#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: schedule_override
short_description: Manage PagerDuty schedule overrides
description:
  - Create or delete overrides on a PagerDuty on-call schedule.
version_added: "1.0.0"
author: PagerDuty Collection Authors
options:
  schedule:
    description: The schedule name or ID.
    type: str
    required: true
  user:
    description: The user name or ID to assign the override to.
    type: str
    required: true
  start:
    description: The start time of the override in ISO 8601 format.
    type: str
    required: true
  end:
    description: The end time of the override in ISO 8601 format.
    type: str
    required: true
  state:
    description: Whether the override should exist.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a schedule override
  pagerduty.pagerduty.schedule_override:
    schedule: Primary On-Call
    user: PUSER123
    start: "2024-06-01T09:00:00-04:00"
    end: "2024-06-02T09:00:00-04:00"
    api_token: "{{ pagerduty_token }}"

- name: Remove a schedule override
  pagerduty.pagerduty.schedule_override:
    schedule: Primary On-Call
    user: PUSER123
    start: "2024-06-01T09:00:00-04:00"
    end: "2024-06-02T09:00:00-04:00"
    state: absent
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
override:
  description: The override object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_id(pd, param, find_path, find_key):
    if param.startswith('P') and len(param) >= 7:
        return param
    obj = pd.client.find_by_name(find_path, find_key, param)
    if not obj:
        pd.fail('{0} not found: {1}'.format(find_key.rstrip('s').capitalize(), param))
    return obj['id']


def find_override(pd, schedule_id, user_id, start, end):
    params = {'since': start, 'until': end}
    try:
        result = pd.client.get('/schedules/{0}/overrides'.format(schedule_id), params=params)
        for o in result.get('overrides', []):
            if o.get('user', {}).get('id') == user_id and o.get('start') == start and o.get('end') == end:
                return o
    except PagerDutyError:
        pass
    return None


def main():
    argument_spec = dict(
        schedule=dict(type='str', required=True),
        user=dict(type='str', required=True),
        start=dict(type='str', required=True),
        end=dict(type='str', required=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        schedule_id = resolve_id(pd, module.params['schedule'], '/schedules', 'schedules')
        user_id = resolve_id(pd, module.params['user'], '/users', 'users')
        start = module.params['start']
        end = module.params['end']

        existing = find_override(pd, schedule_id, user_id, start, end)

        if module.params['state'] == 'present':
            if not existing:
                override_data = {
                    'start': start,
                    'end': end,
                    'user': {'id': user_id, 'type': 'user_reference'},
                }
                if not pd.check_mode:
                    result = pd.client.post(
                        '/schedules/{0}/overrides'.format(schedule_id),
                        {'overrides': [override_data]},
                    )
                    pd.result['override'] = result
                pd.result['changed'] = True
            else:
                pd.result['override'] = existing
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete(
                        '/schedules/{0}/overrides/{1}'.format(schedule_id, existing['id'])
                    )
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
