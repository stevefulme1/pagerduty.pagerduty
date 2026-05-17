#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: maintenance_window_info
short_description: List PagerDuty maintenance windows
author: Ansible PagerDuty Collection Authors (@ansible-collections)
description:
  - Retrieves maintenance windows from PagerDuty.
  - Can filter by service IDs and state (ongoing, future, past).
options:
  service_ids:
    description: Filter to maintenance windows for these service IDs.
    type: list
    elements: str
  state:
    description: Filter by maintenance window state.
    type: str
    choices: [ongoing, future, past, all]
    default: all

  limit:
    description:
      - Maximum number of results to return per request.
      - PagerDuty API default is 25, max is 100.
    type: int
    default: 100
  offset:
    description:
      - Pagination offset (number of records to skip).
      - Used for manual pagination through large result sets.
    type: int
    default: 0
  max_results:
    description:
      - Maximum total number of results to return across all pages.
      - Set to 0 for no limit.
    type: int
    default: 1000
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: List all ongoing maintenance windows
  pagerduty.pagerduty.maintenance_window_info:
    api_token: "{{ pd_token }}"
    state: ongoing
'''

RETURN = r'''
maintenance_windows:
  description: List of maintenance windows.
  type: list
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def main():
    argument_spec = dict(
        service_ids=dict(type='list', elements='str'),
        state=dict(type='str', default='all', choices=['ongoing', 'future', 'past', 'all']),
        **PAGERDUTY_COMMON_ARGS,
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)

    try:
        params = {}
        if module.params['service_ids']:
            for sid in module.params['service_ids']:
                params['service_ids[]'] = sid
        if module.params['state'] != 'all':
            params['filter'] = module.params['state']

        if params.get('limit'):
            qp['limit'] = params['limit']
        if params.get('offset'):
            qp['offset'] = params['offset']
        windows = pd.client.list_all('/maintenance_windows', 'maintenance_windows', params=params)
        pd.result['maintenance_windows'] = windows
    except PagerDutyError as e:
        pd.fail('Failed to list maintenance windows: {0}'.format(str(e)))

    pd.exit()


if __name__ == '__main__':
    main()
