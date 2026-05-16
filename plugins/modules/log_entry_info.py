#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: log_entry_info
short_description: Get PagerDuty log entries
description:
  - Retrieve log entries globally or scoped to a specific incident.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  incident_id:
    description: Scope log entries to a specific incident.
    type: str
  since:
    description: Start of date range (ISO 8601).
    type: str
  until:
    description: End of date range (ISO 8601).
    type: str
  is_overview:
    description: If true, return only overview log entries.
    type: bool
    default: false
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get log entries for an incident
  pagerduty.pagerduty.log_entry_info:
    incident_id: PINC001
  register: result

- name: Get overview log entries from a date range
  pagerduty.pagerduty.log_entry_info:
    since: "2024-01-01T00:00:00Z"
    until: "2024-01-02T00:00:00Z"
    is_overview: true
  register: result
'''

RETURN = r'''
log_entries:
  description: List of log entries.
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
            incident_id=dict(type='str'),
            since=dict(type='str'),
            until=dict(type='str'),
            is_overview=dict(type='bool', default=False),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        path = '/log_entries'
        if params['incident_id']:
            path = '/incidents/{0}/log_entries'.format(params['incident_id'])

        qp = {}
        if params['since']:
            qp['since'] = params['since']
        if params['until']:
            qp['until'] = params['until']
        if params['is_overview']:
            qp['is_overview'] = 'true'
        entries = client.list_all(path, 'log_entries', params=qp or None)
        module.exit_json(changed=False, log_entries=entries)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
