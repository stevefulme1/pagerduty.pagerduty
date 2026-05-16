#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event
short_description: Send PagerDuty events via Events API v2
description:
  - Trigger, acknowledge, or resolve incidents using the PagerDuty Events API v2.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  routing_key:
    description: The integration routing key (Events API v2).
    type: str
    required: true
    no_log: true
  event_action:
    description: The type of event action.
    type: str
    required: true
    choices: [trigger, acknowledge, resolve]
  dedup_key:
    description: Deduplication key for correlating triggers, acks, and resolves.
    type: str
  summary:
    description: A brief text summary of the event. Required for trigger.
    type: str
  source:
    description: The source of the event, typically a hostname or FQDN.
    type: str
  severity:
    description: The severity of the event. Required for trigger.
    type: str
    choices: [critical, error, warning, info]
  component:
    description: The component responsible for the event.
    type: str
  group:
    description: A logical grouping of components.
    type: str
  class_type:
    description: The class/type of the event.
    type: str
  custom_details:
    description: Additional details about the event as a dictionary.
    type: dict
  links:
    description: List of link objects with href and text keys.
    type: list
    elements: dict
  images:
    description: List of image objects with src, href, and alt keys.
    type: list
    elements: dict
'''

EXAMPLES = r'''
- name: Trigger an incident
  pagerduty.pagerduty.event:
    routing_key: "{{ pd_routing_key }}"
    event_action: trigger
    summary: "Server disk usage above 90%"
    source: web-server-01.example.com
    severity: critical
    component: disk
    custom_details:
      disk_usage: "92%"
      mount_point: /data
  register: result

- name: Acknowledge an incident
  pagerduty.pagerduty.event:
    routing_key: "{{ pd_routing_key }}"
    event_action: acknowledge
    dedup_key: "{{ result.dedup_key }}"

- name: Resolve an incident
  pagerduty.pagerduty.event:
    routing_key: "{{ pd_routing_key }}"
    event_action: resolve
    dedup_key: "{{ result.dedup_key }}"
'''

RETURN = r'''
status:
  description: Response status from the Events API.
  type: str
  returned: always
message:
  description: Response message from the Events API.
  type: str
  returned: always
dedup_key:
  description: The deduplication key for the event.
  type: str
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PagerDutyEventsClient, PagerDutyError,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            routing_key=dict(type='str', required=True, no_log=True),
            event_action=dict(type='str', required=True, choices=['trigger', 'acknowledge', 'resolve']),
            dedup_key=dict(type='str'),
            summary=dict(type='str'),
            source=dict(type='str'),
            severity=dict(type='str', choices=['critical', 'error', 'warning', 'info']),
            component=dict(type='str'),
            group=dict(type='str'),
            class_type=dict(type='str'),
            custom_details=dict(type='dict'),
            links=dict(type='list', elements='dict'),
            images=dict(type='list', elements='dict'),
        ),
        required_if=[
            ('event_action', 'trigger', ['summary', 'severity']),
        ],
        supports_check_mode=True,
    )

    params = module.params

    if module.check_mode:
        module.exit_json(changed=True, msg='Event would be sent (check mode)')

    try:
        client = PagerDutyEventsClient(module)

        payload = None
        if params['event_action'] == 'trigger':
            payload = {
                'summary': params['summary'],
                'severity': params['severity'],
                'source': params['source'] or 'ansible',
            }
            for key in ('component', 'group', 'custom_details'):
                if params[key]:
                    payload[key] = params[key]
            if params['class_type']:
                payload['class'] = params['class_type']

        result = client.send_event(
            routing_key=params['routing_key'],
            event_action=params['event_action'],
            dedup_key=params['dedup_key'],
            payload=payload,
            links=params['links'],
            images=params['images'],
        )

        module.exit_json(
            changed=True,
            status=result.get('status', ''),
            message=result.get('message', ''),
            dedup_key=result.get('dedup_key', ''),
        )
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
