#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incident_info
short_description: List or get PagerDuty incidents
description:
  - Retrieve a single incident by ID or list incidents with filters.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific incident to retrieve.
    type: str
  statuses:
    description: Filter by incident statuses.
    type: list
    elements: str
    choices: [triggered, acknowledged, resolved]
  service_ids:
    description: List of service IDs to filter by.
    type: list
    elements: str
  urgencies:
    description: Filter by urgency levels.
    type: list
    elements: str
    choices: [high, low]
  since:
    description: Start of date range (ISO 8601).
    type: str
  until:
    description: End of date range (ISO 8601).
    type: str
  sort_by:
    description: Sort field and direction.
    type: str
    choices: [incident_number:asc, incident_number:desc, created_at:asc, created_at:desc,
              resolved_at:asc, resolved_at:desc, urgency:asc, urgency:desc]
  limit:
    description: Maximum number of results to return per page.
    type: int
    default: 25
  offset:
    description: Offset for pagination.
    type: int
    default: 0
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get a specific incident
  pagerduty.pagerduty.incident_info:
    id: PINC001
  register: result

- name: List all triggered and acknowledged incidents
  pagerduty.pagerduty.incident_info:
    statuses: [triggered, acknowledged]
  register: result

- name: List high-urgency incidents for a service
  pagerduty.pagerduty.incident_info:
    service_ids: ["PSVC01"]
    urgencies: [high]
    since: "2024-01-01T00:00:00Z"
  register: result
'''

RETURN = r'''
incidents:
  description: List of incidents matching the query.
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
            statuses=dict(type='list', elements='str', choices=['triggered', 'acknowledged', 'resolved']),
            service_ids=dict(type='list', elements='str'),
            urgencies=dict(type='list', elements='str', choices=['high', 'low']),
            since=dict(type='str'),
            until=dict(type='str'),
            sort_by=dict(type='str', choices=[
                'incident_number:asc', 'incident_number:desc',
                'created_at:asc', 'created_at:desc',
                'resolved_at:asc', 'resolved_at:desc',
                'urgency:asc', 'urgency:desc',
            ]),
            limit=dict(type='int', default=25),
            offset=dict(type='int', default=0),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        if params['id']:
            inc = client.get('/incidents/{0}'.format(params['id']))
            module.exit_json(changed=False, incidents=[inc.get('incident', inc)])
        else:
            qp = {}
            if params['statuses']:
                qp['statuses[]'] = ','.join(params['statuses'])
            if params['service_ids']:
                qp['service_ids[]'] = ','.join(params['service_ids'])
            if params['urgencies']:
                qp['urgencies[]'] = ','.join(params['urgencies'])
            if params['since']:
                qp['since'] = params['since']
            if params['until']:
                qp['until'] = params['until']
            if params['sort_by']:
                qp['sort_by'] = params['sort_by']
            if params['limit']:
                qp['limit'] = params['limit']
            if params['offset']:
                qp['offset'] = params['offset']
            incidents = client.list_all('/incidents', 'incidents', params=qp or None)
            module.exit_json(changed=False, incidents=incidents)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
