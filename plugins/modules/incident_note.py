#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incident_note
short_description: Add notes to PagerDuty incidents
description:
  - Add a note to an existing PagerDuty incident.
  - This module only supports state=present since notes cannot be deleted.
version_added: "1.0.0"
author: "PagerDuty Collection Authors"
options:
  incident:
    description: The incident ID to add the note to.
    type: str
    required: true
  content:
    description: The note content text.
    type: str
    required: true
  state:
    description: Desired state. Only C(present) is supported.
    type: str
    choices: [present]
    default: present
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Add a note to an incident
  pagerduty.pagerduty.incident_note:
    api_token: "{{ pd_token }}"
    incident: "P1234567"
    content: "Investigating the root cause of the outage."

- name: Add a resolution note
  pagerduty.pagerduty.incident_note:
    api_token: "{{ pd_token }}"
    incident: "P1234567"
    content: "Issue resolved by restarting the application server."
'''

RETURN = r'''
note:
  description: The created note object.
  type: dict
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def main():
    argument_spec = dict(
        incident=dict(type='str', required=True),
        content=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present']),
        **PAGERDUTY_COMMON_ARGS,
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    pd = PagerDutyModule(module)

    try:
        incident_id = module.params['incident']
        content = module.params['content']

        # Verify the incident exists
        existing = pd.client.find_by_id('/incidents/{0}'.format(incident_id), 'incident')
        if not existing:
            pd.fail('Incident {0} not found'.format(incident_id))

        if not pd.check_mode:
            result = pd.client.post(
                '/incidents/{0}/notes'.format(incident_id),
                {'note': {'content': content}}
            )
            pd.result['note'] = result.get('note', result)

        pd.result['changed'] = True
        pd.exit()
    except PagerDutyError as e:
        pd.fail(str(e))


if __name__ == '__main__':
    main()
