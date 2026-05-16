#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: service_integration
short_description: Manage PagerDuty service integrations
description:
  - Create, update, or delete integrations on a PagerDuty service.
version_added: "1.0.0"
author: PagerDuty Collection Authors
options:
  service:
    description: The service name or ID to add the integration to.
    type: str
    required: true
  name:
    description: The name of the integration.
    type: str
    required: true
  type:
    description: The integration type.
    type: str
    required: true
  vendor:
    description: The vendor ID for the integration.
    type: str
  integration_email:
    description: Email address for email-based integrations.
    type: str
  state:
    description: Whether the integration should exist.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create an Events API v2 integration
  pagerduty.pagerduty.service_integration:
    service: My Web App
    name: Ansible Events
    type: events_api_v2_inbound_integration
    api_token: "{{ pagerduty_token }}"

- name: Remove an integration
  pagerduty.pagerduty.service_integration:
    service: My Web App
    name: Ansible Events
    type: events_api_v2_inbound_integration
    state: absent
    api_token: "{{ pagerduty_token }}"
'''

RETURN = r'''
integration:
  description: The integration object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_service(pd, service_param):
    if service_param.startswith('P') and len(service_param) >= 7:
        svc = pd.client.find_by_id('/services/{0}'.format(service_param), 'service')
        if not svc:
            pd.fail('Service not found: {0}'.format(service_param))
        return svc
    svc = pd.client.find_by_name('/services', 'services', service_param)
    if not svc:
        pd.fail('Service not found: {0}'.format(service_param))
    return svc


def find_integration(pd, service_id, name):
    integrations = pd.client.list_all(
        '/services/{0}/integrations'.format(service_id),
        'integrations',
    )
    # list_all may fail on this endpoint; fall back to service GET
    if not integrations:
        svc = pd.client.find_by_id('/services/{0}'.format(service_id), 'service')
        integrations = svc.get('integrations', []) if svc else []
    for i in integrations:
        if i.get('name') == name:
            return i
    return None


def main():
    argument_spec = dict(
        service=dict(type='str', required=True),
        name=dict(type='str', required=True),
        type=dict(type='str', required=True),
        vendor=dict(type='str'),
        integration_email=dict(type='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    argument_spec.update(PAGERDUTY_COMMON_ARGS)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        svc = resolve_service(pd, module.params['service'])
        service_id = svc['id']
        existing = find_integration(pd, service_id, module.params['name'])

        if module.params['state'] == 'present':
            data = {
                'name': module.params['name'],
                'type': module.params['type'],
            }
            if module.params.get('vendor'):
                data['vendor'] = {'id': module.params['vendor'], 'type': 'vendor_reference'}
            if module.params.get('integration_email'):
                data['integration_email'] = module.params['integration_email']

            if existing:
                changes = pd._diff(existing, data, ['name', 'type', 'integration_email'])
                if changes:
                    if not pd.check_mode:
                        result = pd.client.put(
                            '/services/{0}/integrations/{1}'.format(service_id, existing['id']),
                            {'integration': changes},
                        )
                        pd.result['integration'] = result.get('integration', result)
                    else:
                        pd.result['integration'] = existing
                    pd.result['changed'] = True
                else:
                    pd.result['integration'] = existing
            else:
                if not pd.check_mode:
                    result = pd.client.post(
                        '/services/{0}/integrations'.format(service_id),
                        {'integration': data},
                    )
                    pd.result['integration'] = result.get('integration', result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete(
                        '/services/{0}/integrations/{1}'.format(service_id, existing['id'])
                    )
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
