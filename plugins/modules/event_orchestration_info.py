#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: event_orchestration_info
short_description: List or get PagerDuty event orchestrations
description:
  - Retrieve a single event orchestration by ID or name, or list all.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific event orchestration to retrieve.
    type: str
  name:
    description: Filter event orchestrations by exact name match.
    type: str
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get a specific event orchestration
  pagerduty.pagerduty.event_orchestration_info:
    id: PORCH01
  register: result

- name: Find an event orchestration by name
  pagerduty.pagerduty.event_orchestration_info:
    name: Production Events
  register: result
'''

RETURN = r'''
event_orchestrations:
  description: List of event orchestrations matching the query.
  type: list
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyClient, PagerDutyError,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            id=dict(type='str'),
            name=dict(type='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        if params['id']:
            orch = client.get('/event_orchestrations/{0}'.format(params['id']))
            module.exit_json(changed=False, event_orchestrations=[orch.get('orchestration', orch)])
        else:
            orchs = client.list_all('/event_orchestrations', 'orchestrations')
            if params['name']:
                orchs = [o for o in orchs if o.get('name') == params['name']]
            module.exit_json(changed=False, event_orchestrations=orchs)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
