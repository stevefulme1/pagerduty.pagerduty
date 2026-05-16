#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: schedule
short_description: Manage PagerDuty on-call schedules
description:
  - Create, update, or delete PagerDuty on-call schedules.
version_added: "1.0.0"
author: Ansible Ansible PagerDuty Collection Authors (@ansible-collections) (@ansible-collections)
options:
  name:
    description: The name of the schedule.
    type: str
    required: true
  description:
    description: A description for the schedule.
    type: str
  time_zone:
    description: The time zone for the schedule (e.g. America/New_York).
    type: str
    required: true
  schedule_layers:
    description: >
      List of schedule layers. Each layer is a dict with rotation_virtual_start,
      rotation_turn_length_seconds, start, users (list of dicts with user type/id),
      and optional restrictions.
    type: list
    elements: dict
  state:
    description: Whether the schedule should exist.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a weekly on-call schedule
  pagerduty.pagerduty.schedule:
    name: Primary On-Call
    time_zone: America/New_York
    schedule_layers:
      - rotation_virtual_start: "2024-01-01T00:00:00-05:00"
        rotation_turn_length_seconds: 604800
        start: "2024-01-01T00:00:00-05:00"
        users:
          - user:
              type: user_reference
              id: PUSER123
    api_token: "{{ pagerduty_token }}"

- name: Delete a schedule
  pagerduty.pagerduty.schedule:
    name: Primary On-Call
    time_zone: America/New_York
    state: absent
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
schedule:
  description: The schedule object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def build_schedule_data(module):
    data = {
        'name': module.params['name'],
        'type': 'schedule',
        'time_zone': module.params['time_zone'],
    }
    if module.params.get('description') is not None:
        data['description'] = module.params['description']
    if module.params.get('schedule_layers') is not None:
        data['schedule_layers'] = module.params['schedule_layers']
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str'),
        time_zone=dict(type='str', required=True),
        schedule_layers=dict(type='list', elements='dict'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        if module.params['state'] == 'present':
            pd.ensure_present(
                resource_key='schedule',
                find_path='/schedules',
                find_key='schedules',
                create_path='/schedules',
                create_data=build_schedule_data(module),
                update_path_tmpl='/schedules/{id}',
                update_data_fn=lambda: build_schedule_data(module),
                compare_keys=['name', 'description', 'time_zone', 'schedule_layers'],
            )
        else:
            pd.ensure_absent(
                resource_key='schedule',
                find_path='/schedules',
                find_key='schedules',
                delete_path_tmpl='/schedules/{id}',
            )
        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
