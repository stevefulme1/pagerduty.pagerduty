#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: audit_record_info
short_description: Get PagerDuty audit records
description:
  - Retrieve audit trail records with optional filters.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  since:
    description: Start of date range (ISO 8601).
    type: str
  until:
    description: End of date range (ISO 8601).
    type: str
  method_type:
    description: Filter by HTTP method type.
    type: str
  actions:
    description: List of action types to filter by.
    type: list
    elements: str
  root_resource_types:
    description: List of root resource types to filter by.
    type: list
    elements: str
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get audit records for the last day
  pagerduty.pagerduty.audit_record_info:
    since: "2024-01-01T00:00:00Z"
    until: "2024-01-02T00:00:00Z"
  register: result

- name: Get audit records for services
  pagerduty.pagerduty.audit_record_info:
    root_resource_types: [services]
  register: result
'''

RETURN = r'''
records:
  description: List of audit records.
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
            since=dict(type='str'),
            until=dict(type='str'),
            method_type=dict(type='str'),
            actions=dict(type='list', elements='str'),
            root_resource_types=dict(type='list', elements='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        qp = {}
        if params['since']:
            qp['since'] = params['since']
        if params['until']:
            qp['until'] = params['until']
        if params['method_type']:
            qp['method.type'] = params['method_type']
        if params['actions']:
            qp['actions[]'] = ','.join(params['actions'])
        if params['root_resource_types']:
            qp['root_resource_types[]'] = ','.join(params['root_resource_types'])
        records = client.list_all('/audit/records', 'records', params=qp or None)
        module.exit_json(changed=False, records=records)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
