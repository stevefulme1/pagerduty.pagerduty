#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: service_dependency
short_description: Manage PagerDuty service dependencies
description:
  - Create and remove dependencies between PagerDuty services.
  - Supports both technical services and business services.
version_added: "1.0.0"
author: "PagerDuty Collection Authors"
options:
  dependent_service:
    description: Name or ID of the dependent (upstream) service.
    type: str
    required: true
  dependent_service_type:
    description: Type of the dependent service.
    type: str
    choices: [business_service, service]
    default: service
  supporting_service:
    description: Name or ID of the supporting (downstream) service.
    type: str
    required: true
  supporting_service_type:
    description: Type of the supporting service.
    type: str
    choices: [business_service, service]
    default: service
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a service dependency
  pagerduty.pagerduty.service_dependency:
    api_token: "{{ pd_token }}"
    dependent_service: "E-Commerce Platform"
    dependent_service_type: business_service
    supporting_service: "Payment Gateway"
    supporting_service_type: service
    state: present

- name: Remove a service dependency
  pagerduty.pagerduty.service_dependency:
    api_token: "{{ pd_token }}"
    dependent_service: "E-Commerce Platform"
    dependent_service_type: business_service
    supporting_service: "Legacy Payment"
    supporting_service_type: service
    state: absent
'''

RETURN = r'''
dependency:
  description: The dependency relationship object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def resolve_service(client, value, service_type):
    if value.startswith('P') and len(value) >= 7:
        return value
    if service_type == 'business_service':
        found = client.find_by_name('/business_services', 'business_services', value)
    else:
        found = client.find_by_name('/services', 'services', value)
    if not found:
        raise PagerDutyError('Could not find {0} "{1}"'.format(service_type, value))
    return found['id']


def build_relationship(dep_id, dep_type, sup_id, sup_type):
    return {
        'dependent_service': {
            'id': dep_id,
            'type': dep_type + '_reference' if not dep_type.endswith('_reference') else dep_type,
        },
        'supporting_service': {
            'id': sup_id,
            'type': sup_type + '_reference' if not sup_type.endswith('_reference') else sup_type,
        },
        'type': 'service_dependency',
    }


def find_existing_dependency(client, dep_id, dep_type, sup_id):
    """Check if this dependency already exists."""
    try:
        if dep_type == 'business_service':
            path = '/service_dependencies/business_services/{0}'.format(dep_id)
        else:
            path = '/service_dependencies/technical_services/{0}'.format(dep_id)
        result = client.get(path)
        relationships = result.get('relationships', [])
        for rel in relationships:
            supporting = rel.get('supporting_service', {})
            if supporting.get('id') == sup_id:
                return rel
    except PagerDutyError:
        pass
    return None


def main():
    argument_spec = dict(
        dependent_service=dict(type='str', required=True),
        dependent_service_type=dict(type='str', default='service', choices=['business_service', 'service']),
        supporting_service=dict(type='str', required=True),
        supporting_service_type=dict(type='str', default='service', choices=['business_service', 'service']),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    pd = PagerDutyModule(module)
    params = module.params

    try:
        dep_type = params['dependent_service_type']
        sup_type = params['supporting_service_type']
        dep_id = resolve_service(pd.client, params['dependent_service'], dep_type)
        sup_id = resolve_service(pd.client, params['supporting_service'], sup_type)

        relationship = build_relationship(dep_id, dep_type, sup_id, sup_type)
        existing = find_existing_dependency(pd.client, dep_id, dep_type, sup_id)

        if params['state'] == 'absent':
            if existing:
                if not pd.check_mode:
                    pd.client.post('/service_dependencies/disassociate',
                                   {'relationships': [relationship]})
                pd.result['changed'] = True
        else:
            if not existing:
                if not pd.check_mode:
                    result = pd.client.post('/service_dependencies/associate',
                                            {'relationships': [relationship]})
                    relationships = result.get('relationships', [])
                    pd.result['dependency'] = relationships[0] if relationships else result
                pd.result['changed'] = True
            else:
                pd.result['dependency'] = existing

        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
