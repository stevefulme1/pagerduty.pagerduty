#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: analytics_info
short_description: Get PagerDuty analytics data
description:
  - Retrieve analytics metrics for incidents, services, or teams via the Analytics API.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  type:
    description: The type of analytics data to retrieve.
    type: str
    required: true
    choices: [incidents, services, teams]
  filters:
    description:
      - Dictionary of filters to apply.
      - Supported keys include service_ids, team_ids, urgency, created_at_start, created_at_end.
    type: dict
    default: {}
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get incident analytics for a date range
  pagerduty.pagerduty.analytics_info:
    type: incidents
    filters:
      created_at_start: "2024-01-01T00:00:00Z"
      created_at_end: "2024-01-31T23:59:59Z"
  register: result

- name: Get service analytics filtered by team
  pagerduty.pagerduty.analytics_info:
    type: services
    filters:
      team_ids: ["PTEAM01"]
  register: result
'''

RETURN = r'''
data:
  description: Analytics data returned by the API.
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
            type=dict(type='str', required=True, choices=['incidents', 'services', 'teams']),
            filters=dict(type='dict', default={}),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params
    analytics_type = params['type']

    path_map = {
        'incidents': '/analytics/metrics/incidents/all',
        'services': '/analytics/metrics/incidents/services',
        'teams': '/analytics/metrics/incidents/teams',
    }

    try:
        body = {}
        filters = params['filters']
        if filters:
            body['filters'] = filters
        result = client.post(path_map[analytics_type], body)
        module.exit_json(changed=False, data=result.get('data', []),
                         filters=result.get('filters', {}),
                         aggregate_unit=result.get('aggregate_unit', ''))
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
