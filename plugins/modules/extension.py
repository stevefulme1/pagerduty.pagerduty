#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: extension
short_description: Manage PagerDuty extensions
description:
  - Create, update, and delete extensions (webhooks on services) in PagerDuty.
version_added: "1.0.0"
author: PagerDuty Ansible Collection Authors
options:
  name:
    description: The name of the extension.
    type: str
    required: true
  endpoint_url:
    description: The URL to receive webhook callbacks.
    type: str
  extension_schema:
    description: The ID or type of the extension schema (e.g. webhook_generic_v2).
    type: str
    default: webhook_generic_v2
  services:
    description: List of service IDs to attach the extension to.
    type: list
    elements: str
    default: []
  state:
    description: Whether the extension should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a generic webhook extension
  pagerduty.pagerduty.extension:
    api_token: "{{ pd_token }}"
    name: "My Webhook"
    endpoint_url: "https://example.com/webhook"
    extension_schema: webhook_generic_v2
    services:
      - PXXXXXX
    state: present

- name: Remove an extension
  pagerduty.pagerduty.extension:
    api_token: "{{ pd_token }}"
    name: "My Webhook"
    state: absent
'''

RETURN = r'''
extension:
  description: The extension object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def build_create_data(module):
    """Build the extension creation payload."""
    service_refs = [{'id': s, 'type': 'service_reference'} for s in module.params['services']]
    schema_id = module.params['extension_schema']
    return {
        'name': module.params['name'],
        'endpoint_url': module.params['endpoint_url'],
        'extension_schema': {'id': schema_id, 'type': 'extension_schema_reference'},
        'extension_objects': service_refs,
        'type': 'extension',
    }


def build_update_data(module):
    """Build the extension update payload."""
    data = {'name': module.params['name'], 'type': 'extension'}
    if module.params['endpoint_url']:
        data['endpoint_url'] = module.params['endpoint_url']
    if module.params['services']:
        data['extension_objects'] = [{'id': s, 'type': 'service_reference'} for s in module.params['services']]
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        endpoint_url=dict(type='str'),
        extension_schema=dict(type='str', default='webhook_generic_v2'),
        services=dict(type='list', elements='str', default=[]),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        if state == 'present':
            pd.ensure_present(
                resource_key='extension',
                find_path='/extensions',
                find_key='extensions',
                create_path='/extensions',
                create_data=build_create_data(module),
                update_path_tmpl='/extensions/{id}',
                update_data_fn=lambda: build_update_data(module),
                compare_keys=['name', 'endpoint_url', 'extension_objects'],
            )
        else:
            pd.ensure_absent(
                resource_key='extension',
                find_path='/extensions',
                find_key='extensions',
                delete_path_tmpl='/extensions/{id}',
            )
        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
