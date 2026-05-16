#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: change_event
short_description: Send PagerDuty change events
description:
  - Send change events to PagerDuty to track deployments, config changes, and other operational events.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  routing_key:
    description: The integration routing key (Events API v2).
    type: str
    required: true
    no_log: true
  summary:
    description: A brief text summary of the change.
    type: str
    required: true
  timestamp:
    description: When the change occurred (ISO 8601). Defaults to now.
    type: str
  source:
    description: The source of the change event.
    type: str
  custom_details:
    description: Additional details about the change as a dictionary.
    type: dict
  links:
    description: List of link objects with href and text keys.
    type: list
    elements: dict
'''

EXAMPLES = r'''
- name: Send a deployment change event
  pagerduty.pagerduty.change_event:
    routing_key: "{{ pd_routing_key }}"
    summary: "Deployed v2.1.0 to production"
    source: deploy-pipeline
    custom_details:
      version: "2.1.0"
      environment: production
      deployer: ansible
    links:
      - href: "https://github.com/org/repo/releases/tag/v2.1.0"
        text: "Release notes"
  register: result

- name: Send a config change event
  pagerduty.pagerduty.change_event:
    routing_key: "{{ pd_routing_key }}"
    summary: "Updated nginx configuration on web-01"
    source: ansible-playbook
'''

RETURN = r'''
status:
  description: Response status from the Change Events API.
  type: str
  returned: always
message:
  description: Response message from the Change Events API.
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
            summary=dict(type='str', required=True),
            timestamp=dict(type='str'),
            source=dict(type='str'),
            custom_details=dict(type='dict'),
            links=dict(type='list', elements='dict'),
        ),
        supports_check_mode=True,
    )

    params = module.params

    if module.check_mode:
        module.exit_json(changed=True, msg='Change event would be sent (check mode)')

    try:
        client = PagerDutyEventsClient(module)

        result = client.send_change(
            routing_key=params['routing_key'],
            summary=params['summary'],
            timestamp=params['timestamp'],
            source=params['source'],
            custom_details=params['custom_details'],
            links=params['links'],
        )

        module.exit_json(
            changed=True,
            status=result.get('status', ''),
            message=result.get('message', ''),
        )
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
