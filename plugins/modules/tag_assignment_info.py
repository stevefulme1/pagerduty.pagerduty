#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: tag_assignment_info
short_description: List tag assignments in PagerDuty
description:
  - Retrieve information about PagerDuty tags.
  - This is a read-only module that does not modify any resources.
  - Returns a list of matching resources with full metadata.
  - Supports check mode (read-only, no changes are made).
  - Uses the PagerDuty REST API v2.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  entity_type:
    description: Filter by entity type.
    type: str
  entity_id:
    description: The entity ID to list tags for.
    type: str
notes:
  - This module requires a valid PagerDuty API token.
  - All timestamps are returned in ISO 8601 format.
  - Pagination is handled automatically for list operations.
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: List all tags
  pagerduty.pagerduty.tag_assignment_info:
  register: result
'''

RETURN = r'''
tags:
  description: List of tags matching the query.
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
            entity_type=dict(type='str'),
            entity_id=dict(type='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        qp = {}
        if params.get('entity_type'):
            qp['entity_type'] = params['entity_type']
        if params.get('entity_id'):
            qp['entity_id'] = params['entity_id']
        data = client.list_all('/tags', 'tags', params=qp or None)
        module.exit_json(changed=False, tags=data, count=len(data))
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
