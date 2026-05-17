#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: service_info
short_description: List or get PagerDuty services
description:
  - Retrieve a single service by ID or name, or list all services with optional filters.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific service to retrieve.
    type: str
  name:
    description: Filter services by exact name match.
    type: str
  team_ids:
    description: List of team IDs to filter services by.
    type: list
    elements: str
  include:
    description: Additional data to include in the response.
    type: list
    elements: str
    choices: [integrations, escalation_policies]
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
- name: Get a specific service
  pagerduty.pagerduty.service_info:
    id: PABC123
  register: result

- name: Find a service by name
  pagerduty.pagerduty.service_info:
    name: My Web App
  register: result

- name: List all services for a team with integrations
  pagerduty.pagerduty.service_info:
    team_ids: ["PTEAM01"]
    include: [integrations]
  register: result
'''

RETURN = r'''
services:
  description: List of services matching the query.
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
            team_ids=dict(type='list', elements='str'),
            include=dict(type='list', elements='str', choices=['integrations', 'escalation_policies']),
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
            qp = {}
            if params['include']:
                qp['include[]'] = ','.join(params['include'])
            svc = client.get('/services/{0}'.format(params['id']), params=qp or None)
            module.exit_json(changed=False, services=[svc.get('service', svc)])
        else:
            qp = {}
            if params['name']:
                qp['query'] = params['name']
            if params['team_ids']:
                qp['team_ids[]'] = ','.join(params['team_ids'])
            if params['include']:
                qp['include[]'] = ','.join(params['include'])
            if params['limit']:
                qp['limit'] = params['limit']
            if params['offset']:
                qp['offset'] = params['offset']
            services = client.list_all('/services', 'services', params=qp or None)
            if params['name']:
                services = [s for s in services if s.get('name') == params['name']]
            module.exit_json(changed=False, services=services)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
