#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: status_page
short_description: Manage PagerDuty status pages
description:
  - Create, update, and delete status pages in PagerDuty.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  id:
    description: The ID of the status page to update or delete.
    type: str
  name:
    description: The name of the status page.
    type: str
    required: true
  url:
    description: The custom URL slug for the status page.
    type: str
  type:
    description: The type of status page.
    type: str
    default: public
    choices: [public, private]
  service_ids:
    description: List of service IDs to display on the status page.
    type: list
    elements: str
    default: []
  state:
    description: Whether the status page should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a public status page
  pagerduty.pagerduty.status_page:
    api_token: "{{ pd_token }}"
    name: "Service Status"
    url: "status"
    type: public
    service_ids:
      - PSVC01
      - PSVC02
    state: present

- name: Delete a status page
  pagerduty.pagerduty.status_page:
    api_token: "{{ pd_token }}"
    name: "Old Status Page"
    id: PSTATPG01
    state: absent
'''

RETURN = r'''
status_page:
  description: The status page object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)

API_PATH = '/status_pages'
RESOURCE_KEY = 'status_page'
LIST_KEY = 'status_pages'


def find_by_name(pd, name):
    """Find a status page by name."""
    try:
        pages = pd.client.list_all(API_PATH, LIST_KEY)
    except PagerDutyError:
        return None
    for page in pages:
        if page.get('name') == name:
            return page
    return None


def build_payload(module):
    """Build the status page payload."""
    data = {
        'name': module.params['name'],
        'type': module.params['type'],
    }
    if module.params['url']:
        data['url_slug'] = module.params['url']
    if module.params['service_ids']:
        data['service_ids'] = module.params['service_ids']
    return data


def main():
    argument_spec = dict(
        id=dict(type='str'),
        name=dict(type='str', required=True),
        url=dict(type='str'),
        type=dict(type='str', default='public', choices=['public', 'private']),
        service_ids=dict(type='list', elements='str', default=[]),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        existing = None
        if module.params['id']:
            existing = pd.client.find_by_id('{0}/{1}'.format(API_PATH, module.params['id']), RESOURCE_KEY)
        else:
            existing = find_by_name(pd, module.params['name'])

        if state == 'present':
            payload = build_payload(module)
            if existing:
                if not pd.check_mode:
                    result = pd.client.put(
                        '{0}/{1}'.format(API_PATH, existing['id']),
                        {RESOURCE_KEY: payload},
                    )
                    pd.result[RESOURCE_KEY] = result.get(RESOURCE_KEY, result)
                else:
                    pd.result[RESOURCE_KEY] = existing
                pd.result['changed'] = True
            else:
                if not pd.check_mode:
                    result = pd.client.post(API_PATH, {RESOURCE_KEY: payload})
                    pd.result[RESOURCE_KEY] = result.get(RESOURCE_KEY, result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete('{0}/{1}'.format(API_PATH, existing['id']))
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
