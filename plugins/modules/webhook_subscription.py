#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: webhook_subscription
short_description: Manage PagerDuty V3 webhook subscriptions
description:
  - Create, update, and delete V3 webhook subscriptions in PagerDuty.
  - Webhook subscriptions send HTTP callbacks when events occur.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  description:
    description: A short description of the webhook subscription.
    type: str
    required: true
  delivery_method_type:
    description: The delivery method type.
    type: str
    default: http_delivery_method
    choices: [http_delivery_method]
  delivery_method_url:
    description: The URL to receive webhook callbacks.
    type: str
    required: true
  events:
    description: List of event type strings to subscribe to.
    type: list
    elements: str
    required: true
  filter_type:
    description: The type of filter for the subscription.
    type: str
    choices: [account_reference, service_reference]
    default: account_reference
  filter_id:
    description: The ID of the service to filter on. Required when filter_type is service_reference.
    type: str
  state:
    description: Whether the webhook subscription should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a webhook subscription
  pagerduty.pagerduty.webhook_subscription:
    api_token: "{{ pd_token }}"
    description: "Incident notifications"
    delivery_method_url: "https://example.com/webhooks/pd"
    events:
      - incident.triggered
      - incident.acknowledged
      - incident.resolved
    filter_type: account_reference
    state: present

- name: Create a service-scoped webhook
  pagerduty.pagerduty.webhook_subscription:
    api_token: "{{ pd_token }}"
    description: "Service webhook"
    delivery_method_url: "https://example.com/webhooks/pd"
    events:
      - incident.triggered
    filter_type: service_reference
    filter_id: PXXXXXX
    state: present

- name: Remove a webhook subscription
  pagerduty.pagerduty.webhook_subscription:
    api_token: "{{ pd_token }}"
    description: "Incident notifications"
    delivery_method_url: "https://example.com/webhooks/pd"
    events: []
    state: absent
'''

RETURN = r'''
webhook_subscription:
  description: The webhook subscription object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def find_subscription(pd, description, url):
    """Find a webhook subscription by description and URL."""
    try:
        subs = pd.client.list_all('/webhook_subscriptions', 'webhook_subscriptions')
    except PagerDutyError:
        return None
    for sub in subs:
        dm = sub.get('delivery_method', {})
        if sub.get('description') == description and dm.get('url') == url:
            return sub
    return None


def build_payload(module):
    """Build the webhook subscription payload."""
    delivery_method = {
        'type': module.params['delivery_method_type'],
        'url': module.params['delivery_method_url'],
    }
    event_list = [{'type': e} for e in module.params['events']]
    sub_filter = {'type': module.params['filter_type']}
    if module.params['filter_id']:
        sub_filter['id'] = module.params['filter_id']
    return {
        'description': module.params['description'],
        'delivery_method': delivery_method,
        'events': event_list,
        'filter': sub_filter,
        'type': 'webhook_subscription',
    }


def main():
    argument_spec = dict(
        description=dict(type='str', required=True),
        delivery_method_type=dict(type='str', default='http_delivery_method', choices=['http_delivery_method']),
        delivery_method_url=dict(type='str', required=True),
        events=dict(type='list', elements='str', required=True),
        filter_type=dict(type='str', default='account_reference', choices=['account_reference', 'service_reference']),
        filter_id=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        existing = find_subscription(pd, module.params['description'], module.params['delivery_method_url'])

        if state == 'present':
            payload = build_payload(module)
            if existing:
                if not pd.check_mode:
                    result = pd.client.put(
                        '/webhook_subscriptions/{0}'.format(existing['id']),
                        {'webhook_subscription': payload},
                    )
                    pd.result['webhook_subscription'] = result.get('webhook_subscription', result)
                else:
                    pd.result['webhook_subscription'] = existing
                pd.result['changed'] = True
            else:
                if not pd.check_mode:
                    result = pd.client.post('/webhook_subscriptions', {'webhook_subscription': payload})
                    pd.result['webhook_subscription'] = result.get('webhook_subscription', result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete('/webhook_subscriptions/{0}'.format(existing['id']))
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
