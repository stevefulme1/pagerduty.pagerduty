#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: service
short_description: Manage PagerDuty services
description:
  - Create, update, or delete PagerDuty services.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  name:
    description: The name of the service.
    type: str
    required: true
  description:
    description: A description for the service.
    type: str
  escalation_policy:
    description: The escalation policy name or ID.
    type: str
    required: true
  alert_creation:
    description: How alerts are created on the service.
    type: str
    choices: [create_alerts_and_incidents, create_incidents]
    default: create_alerts_and_incidents
  alert_grouping_parameters:
    description: Alert grouping parameters as a dict with type and config keys.
    type: dict
  auto_resolve_timeout:
    description: Seconds before an incident auto-resolves. Null to disable.
    type: int
  acknowledgement_timeout:
    description: Seconds before an acknowledged incident re-triggers. Null to disable.
    type: int
  status:
    description: The current status of the service.
    type: str
    choices: [active, warning, critical, maintenance, disabled]
  state:
    description: Whether the service should exist.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a service
  pagerduty.pagerduty.service:
    name: My Web App
    description: Production web application
    escalation_policy: Default
    alert_creation: create_alerts_and_incidents
    api_token: "{{ pagerduty_token }}"

- name: Delete a service
  pagerduty.pagerduty.service:
    name: My Web App
    escalation_policy: Default
    state: absent
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
service:
  description: The service object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_escalation_policy(pd, ep_param):
    if ep_param.startswith('P') and len(ep_param) >= 7:
        return {'id': ep_param, 'type': 'escalation_policy_reference'}
    ep = pd.client.find_by_name('/escalation_policies', 'escalation_policies', ep_param)
    if not ep:
        pd.fail('Escalation policy not found: {0}'.format(ep_param))
    return {'id': ep['id'], 'type': 'escalation_policy_reference'}


def build_service_data(pd):
    params = pd.module.params
    data = {
        'name': params['name'],
        'escalation_policy': resolve_escalation_policy(pd, params['escalation_policy']),
        'alert_creation': params['alert_creation'],
    }
    if params.get('description') is not None:
        data['description'] = params['description']
    if params.get('alert_grouping_parameters') is not None:
        data['alert_grouping_parameters'] = params['alert_grouping_parameters']
    if params.get('auto_resolve_timeout') is not None:
        data['auto_resolve_timeout'] = params['auto_resolve_timeout']
    if params.get('acknowledgement_timeout') is not None:
        data['acknowledgement_timeout'] = params['acknowledgement_timeout']
    if params.get('status') is not None:
        data['status'] = params['status']
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str'),
        escalation_policy=dict(type='str', required=True),
        alert_creation=dict(type='str', choices=['create_alerts_and_incidents', 'create_incidents'],
                            default='create_alerts_and_incidents'),
        alert_grouping_parameters=dict(type='dict'),
        auto_resolve_timeout=dict(type='int'),
        acknowledgement_timeout=dict(type='int'),
        status=dict(type='str', choices=['active', 'warning', 'critical', 'maintenance', 'disabled']),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        if module.params['state'] == 'present':
            pd.ensure_present(
                resource_key='service',
                find_path='/services',
                find_key='services',
                create_path='/services',
                create_data=build_service_data(pd),
                update_path_tmpl='/services/{id}',
                update_data_fn=lambda: build_service_data(pd),
                compare_keys=['name', 'description', 'escalation_policy', 'alert_creation',
                              'alert_grouping_parameters', 'auto_resolve_timeout',
                              'acknowledgement_timeout', 'status'],
            )
        else:
            pd.ensure_absent(
                resource_key='service',
                find_path='/services',
                find_key='services',
                delete_path_tmpl='/services/{id}',
            )
        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
