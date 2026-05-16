#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: tag_info
short_description: List PagerDuty tags or get entity tags
description:
  - List all tags, get a specific tag by ID or label, or get tags for an entity.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  id:
    description: The ID of a specific tag to retrieve.
    type: str
  label:
    description: Filter tags by exact label match.
    type: str
  entity_type:
    description: Entity type to get tags for. Required with entity_id.
    type: str
    choices: [users, teams, escalation_policies]
  entity_id:
    description: Entity ID to get tags for. Required with entity_type.
    type: str
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: List all tags
  pagerduty.pagerduty.tag_info:
  register: result

- name: Get tags for a specific user
  pagerduty.pagerduty.tag_info:
    entity_type: users
    entity_id: PUSER01
  register: result

- name: Find a tag by label
  pagerduty.pagerduty.tag_info:
    label: production
  register: result
'''

RETURN = r'''
tags:
  description: List of tags matching the query.
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
            label=dict(type='str'),
            entity_type=dict(type='str', choices=['users', 'teams', 'escalation_policies']),
            entity_id=dict(type='str'),
            **PAGERDUTY_COMMON_ARGS
        ),
        required_together=[('entity_type', 'entity_id')],
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    params = module.params

    try:
        if params['id']:
            tag = client.get('/tags/{0}'.format(params['id']))
            module.exit_json(changed=False, tags=[tag.get('tag', tag)])
        elif params['entity_type'] and params['entity_id']:
            path = '/{0}/{1}/tags'.format(params['entity_type'], params['entity_id'])
            tags = client.list_all(path, 'tags')
            module.exit_json(changed=False, tags=tags)
        else:
            qp = {}
            if params['label']:
                qp['query'] = params['label']
            tags = client.list_all('/tags', 'tags', params=qp or None)
            if params['label']:
                tags = [t for t in tags if t.get('label') == params['label']]
            module.exit_json(changed=False, tags=tags)
    except PagerDutyError as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
