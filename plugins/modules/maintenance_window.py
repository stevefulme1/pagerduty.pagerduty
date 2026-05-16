#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: maintenance_window
short_description: Manage PagerDuty maintenance windows
description:
  - Create, update, and delete PagerDuty maintenance windows.
  - Maintenance windows temporarily disable alerts for specified services.
version_added: "1.0.0"
author: "PagerDuty Collection Authors"
options:
  id:
    description: Maintenance window ID for updates or deletion.
    type: str
  description:
    description: Description of the maintenance window.
    type: str
  start_time:
    description:
      - Start time in ISO 8601 format.
      - Required when creating a maintenance window.
    type: str
  end_time:
    description:
      - End time in ISO 8601 format.
      - Required when creating a maintenance window.
    type: str
  services:
    description:
      - List of service names or IDs to include in the maintenance window.
      - Required when creating a maintenance window.
    type: list
    elements: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a maintenance window
  pagerduty.pagerduty.maintenance_window:
    api_token: "{{ pd_token }}"
    description: "Scheduled deployment window"
    start_time: "2024-12-01T02:00:00Z"
    end_time: "2024-12-01T04:00:00Z"
    services:
      - "Web Application"
      - "API Gateway"
    state: present

- name: Delete a maintenance window
  pagerduty.pagerduty.maintenance_window:
    api_token: "{{ pd_token }}"
    id: "P1234567"
    state: absent
'''

RETURN = r'''
maintenance_window:
  description: The maintenance window object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_services(client, services):
    refs = []
    for svc in services:
        if svc.startswith('P') and len(svc) >= 7:
            refs.append({'id': svc, 'type': 'service_reference'})
        else:
            found = client.find_by_name('/services', 'services', svc)
            if not found:
                raise PagerDutyError('Could not find service "{0}"'.format(svc))
            refs.append({'id': found['id'], 'type': 'service_reference'})
    return refs


def find_window_by_description(client, description, services):
    """Find an existing maintenance window by description and service overlap."""
    params = {'filter': 'future'}
    windows = client.list_all('/maintenance_windows', 'maintenance_windows', params=params)
    for w in windows:
        if w.get('description') == description:
            return w
    return None


def main():
    argument_spec = dict(
        id=dict(type='str'),
        description=dict(type='str'),
        start_time=dict(type='str'),
        end_time=dict(type='str'),
        services=dict(type='list', elements='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ('start_time', 'end_time', 'services')),
            ('state', 'absent', ('id',)),
        ],
    )

    pd = PagerDutyModule(module)
    params = module.params
    path = '/maintenance_windows'

    try:
        if params['state'] == 'absent':
            window_id = params['id']
            existing = pd.client.find_by_id('{0}/{1}'.format(path, window_id), 'maintenance_window')
            if existing:
                if not pd.check_mode:
                    pd.client.delete('{0}/{1}'.format(path, window_id))
                pd.result['changed'] = True
        else:
            service_refs = resolve_services(pd.client, params['services'])
            create_data = {
                'type': 'maintenance_window',
                'start_time': params['start_time'],
                'end_time': params['end_time'],
                'services': service_refs,
            }
            if params.get('description'):
                create_data['description'] = params['description']

            existing = None
            if params.get('id'):
                existing = pd.client.find_by_id(
                    '{0}/{1}'.format(path, params['id']), 'maintenance_window'
                )
            elif params.get('description'):
                existing = find_window_by_description(pd.client, params['description'], service_refs)

            if existing:
                changes = {}
                for key in ['start_time', 'end_time', 'description']:
                    if params.get(key) and existing.get(key) != params[key]:
                        changes[key] = params[key]

                current_svc_ids = sorted([s['id'] for s in existing.get('services', [])])
                desired_svc_ids = sorted([s['id'] for s in service_refs])
                if current_svc_ids != desired_svc_ids:
                    changes['services'] = service_refs

                if changes:
                    changes['type'] = 'maintenance_window'
                    if not pd.check_mode:
                        result = pd.client.put(
                            '{0}/{1}'.format(path, existing['id']),
                            {'maintenance_window': changes}
                        )
                        pd.result['maintenance_window'] = result.get('maintenance_window', result)
                    pd.result['changed'] = True
                else:
                    pd.result['maintenance_window'] = existing
            else:
                if not pd.check_mode:
                    result = pd.client.post(path, {'maintenance_window': create_data})
                    pd.result['maintenance_window'] = result.get('maintenance_window', result)
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
