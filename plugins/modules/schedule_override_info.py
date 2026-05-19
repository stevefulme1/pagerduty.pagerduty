#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: schedule_override_info
short_description: List overrides for a PagerDuty schedule
description:
  - Retrieve information about PagerDuty overrides.
  - This is a read-only module that does not modify any resources.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  schedule_id:
    description: The ID of the schedule.
    type: str
    required: true
  since:
    description: Start date for overrides (ISO 8601).
    type: str
  until:
    description: End date for overrides (ISO 8601).
    type: str
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: List all overrides
  pagerduty.pagerduty.schedule_override_info:
    schedule_id: EXAMPLE_ID
  register: result
'''

RETURN = r'''
overrides:
  description: List of overrides matching the query.
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the resource.
      type: str
      returned: always
    type:
      description: The PagerDuty resource type.
      type: str
      returned: always
    summary:
      description: A short summary of the resource.
      type: str
      returned: when available
    self:
      description: The API URL for this resource.
      type: str
      returned: always
    html_url:
      description: The URL to view this resource in the PagerDuty web UI.
      type: str
      returned: when available
count:
  description: Number of results returned.
  type: int
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyClient, PagerDutyError,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            schedule_id=dict(type='str', required=True),
            since=dict(type='str'),
            until=dict(type='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        qp = {}
        if params.get('since'):
            qp['since'] = params['since']
        if params.get('until'):
            qp['until'] = params['until']
        data = client.list_all('/schedules/' + params['schedule_id'] + '/overrides', 'overrides', params=qp or None)
        module.exit_json(changed=False, overrides=data, count=len(data))
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
