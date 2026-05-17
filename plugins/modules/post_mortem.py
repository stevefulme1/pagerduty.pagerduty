#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: post_mortem
short_description: Manage PagerDuty post-incident reviews
description:
  - Create and update post-mortem reports for PagerDuty incidents.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  incident_id:
    description: The ID of the incident to create a post-mortem for.
    type: str
    required: true
  description:
    description: A summary description of the post-mortem.
    type: str
  report_url:
    description: URL to the full post-mortem report.
    type: str
  analysis:
    description: Root cause analysis text.
    type: str
  state:
    description: Whether the post-mortem should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a post-mortem
  pagerduty.pagerduty.post_mortem:
    api_token: "{{ pd_token }}"
    incident_id: PINC001
    description: "Database failover caused outage"
    analysis: "Root cause was a missed health check configuration."
    report_url: "https://wiki.example.com/postmortems/pinc001"
    state: present

- name: Delete a post-mortem
  pagerduty.pagerduty.post_mortem:
    api_token: "{{ pd_token }}"
    incident_id: PINC001
    state: absent
'''

RETURN = r'''
post_mortem:
  description: The post-mortem object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def build_payload(module):
    """Build the post-mortem payload."""
    data = {}
    if module.params['description']:
        data['description'] = module.params['description']
    if module.params['report_url']:
        data['report_url'] = module.params['report_url']
    if module.params['analysis']:
        data['analysis'] = module.params['analysis']
    return data


def main():
    argument_spec = dict(
        incident_id=dict(type='str', required=True),
        description=dict(type='str'),
        report_url=dict(type='str'),
        analysis=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']
    incident_id = module.params['incident_id']
    api_path = '/incidents/{0}/postmortem'.format(incident_id)

    try:
        existing = None
        try:
            result = pd.client.get(api_path)
            existing = result.get('postmortem', result) if result else None
        except PagerDutyError as e:
            if e.status_code != 404:
                raise

        if state == 'present':
            payload = build_payload(module)
            if existing:
                if not pd.check_mode:
                    result = pd.client.put(api_path, {'postmortem': payload})
                    pd.result['post_mortem'] = result.get('postmortem', result)
                else:
                    pd.result['post_mortem'] = existing
                pd.result['changed'] = True
            else:
                if not pd.check_mode:
                    result = pd.client.post(api_path, {'postmortem': payload})
                    pd.result['post_mortem'] = result.get('postmortem', result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete(api_path)
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
