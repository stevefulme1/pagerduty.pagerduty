#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: tag_assignment
short_description: Assign or remove PagerDuty tags from entities
description:
  - Assign or remove tags from users, teams, or escalation policies.
  - Uses the PagerDuty tagging API.
version_added: "1.0.0"
author: PagerDuty Ansible Collection Authors
options:
  tag:
    description: The tag label or ID to assign.
    type: str
    required: true
  entity_type:
    description: The type of entity to tag.
    type: str
    required: true
    choices: [users, teams, escalation_policies]
  entity:
    description: The name or ID of the entity to tag.
    type: str
    required: true
  state:
    description: Whether the tag should be assigned or removed.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Assign a tag to a team
  pagerduty.pagerduty.tag_assignment:
    api_token: "{{ pd_token }}"
    tag: "production"
    entity_type: teams
    entity: "Platform Team"
    state: present

- name: Remove a tag from a user
  pagerduty.pagerduty.tag_assignment:
    api_token: "{{ pd_token }}"
    tag: "on-call"
    entity_type: users
    entity: PXXXXXX
    state: absent
'''

RETURN = r'''
changed:
  description: Whether the tag assignment was changed.
  returned: always
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)

ENTITY_TYPE_MAP = {
    'users': ('users', 'user_reference'),
    'teams': ('teams', 'team_reference'),
    'escalation_policies': ('escalation_policies', 'escalation_policy_reference'),
}


def resolve_tag(pd, tag_input):
    """Resolve a tag label or ID to a tag object."""
    if tag_input.startswith('P') and len(tag_input) == 7:
        existing = pd.client.find_by_id('/tags/{0}'.format(tag_input), 'tag')
        if existing:
            return existing
    params = {'query': tag_input}
    tags = pd.client.list_all('/tags', 'tags', params=params)
    for t in tags:
        if t.get('label') == tag_input:
            return t
    return None


def resolve_entity(pd, entity_type, entity_input):
    """Resolve an entity name or ID to its ID."""
    api_path = '/{0}'.format(entity_type)
    ref_type = ENTITY_TYPE_MAP[entity_type][1]
    # Try as ID first
    existing = pd.client.find_by_id('{0}/{1}'.format(api_path, entity_input), entity_type.rstrip('s'))
    if existing:
        return existing.get('id', entity_input)
    # Try by name
    found = pd.client.find_by_name(api_path, entity_type, entity_input)
    if found:
        return found['id']
    return None


def get_entity_tags(pd, entity_type, entity_id):
    """Get tags currently assigned to an entity."""
    path = '/{0}/{1}/tags'.format(entity_type, entity_id)
    try:
        return pd.client.list_all(path, 'tags')
    except PagerDutyError:
        return []


def main():
    argument_spec = dict(
        tag=dict(type='str', required=True),
        entity_type=dict(type='str', required=True, choices=['users', 'teams', 'escalation_policies']),
        entity=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        tag_obj = resolve_tag(pd, module.params['tag'])
        if not tag_obj and state == 'present':
            pd.fail('Tag not found: {0}. Create it first with the tag module.'.format(module.params['tag']))
        if not tag_obj and state == 'absent':
            pd.exit()
            return

        entity_id = resolve_entity(pd, module.params['entity_type'], module.params['entity'])
        if not entity_id:
            pd.fail('Entity not found: {0}'.format(module.params['entity']))

        current_tags = get_entity_tags(pd, module.params['entity_type'], entity_id)
        tag_assigned = any(t['id'] == tag_obj['id'] for t in current_tags)

        if state == 'present' and not tag_assigned:
            if not pd.check_mode:
                pd.client.post(
                    '/{0}/{1}/change_tags'.format(module.params['entity_type'], entity_id),
                    {'add': [{'type': 'tag_reference', 'id': tag_obj['id']}], 'remove': []},
                )
            pd.result['changed'] = True
        elif state == 'absent' and tag_assigned:
            if not pd.check_mode:
                pd.client.post(
                    '/{0}/{1}/change_tags'.format(module.params['entity_type'], entity_id),
                    {'add': [], 'remove': [{'type': 'tag_reference', 'id': tag_obj['id']}]},
                )
            pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
