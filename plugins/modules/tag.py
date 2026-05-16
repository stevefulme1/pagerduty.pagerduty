#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: tag
short_description: Manage PagerDuty tags
description:
  - Create and delete tags in PagerDuty.
  - Tags can be assigned to users, teams, and escalation policies.
version_added: "1.0.0"
author: PagerDuty Ansible Collection Authors
options:
  label:
    description: The label for the tag.
    type: str
    required: true
  state:
    description: Whether the tag should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a tag
  pagerduty.pagerduty.tag:
    api_token: "{{ pd_token }}"
    label: "production"
    state: present

- name: Delete a tag
  pagerduty.pagerduty.tag:
    api_token: "{{ pd_token }}"
    label: "deprecated"
    state: absent
'''

RETURN = r'''
tag:
  description: The tag object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def find_tag_by_label(pd, label):
    """Find a tag by its label."""
    params = {'query': label}
    tags = pd.client.list_all('/tags', 'tags', params=params)
    for tag in tags:
        if tag.get('label') == label:
            return tag
    return None


def main():
    argument_spec = dict(
        label=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']
    label = module.params['label']

    try:
        existing = find_tag_by_label(pd, label)

        if state == 'present':
            if existing:
                pd.result['tag'] = existing
            else:
                if not pd.check_mode:
                    result = pd.client.post('/tags', {'tag': {'type': 'tag', 'label': label}})
                    pd.result['tag'] = result.get('tag', result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete('/tags/{0}'.format(existing['id']))
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
