#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: post_mortem_info
short_description: Get PagerDuty post-mortem info
description:
  - Retrieve post-mortem report details for a PagerDuty incident.
version_added: "1.0.0"
author: "PagerDuty (@PagerDuty)"
options:
  incident_id:
    description: The ID of the incident to retrieve the post-mortem for.
    type: str
    required: true
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Get post-mortem for an incident
  pagerduty.pagerduty.post_mortem_info:
    incident_id: PINC001
  register: result
'''

RETURN = r'''
post_mortem:
  description: The post-mortem report object.
  type: dict
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyClient, PagerDutyError,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            incident_id=dict(type='str', required=True),
            **PAGERDUTY_COMMON_ARGS
        ),
        supports_check_mode=True,
    )

    client = PagerDutyClient(module)
    incident_id = module.params['incident_id']

    try:
        result = client.get('/incidents/{0}/postmortem'.format(incident_id))
        post_mortem = result.get('postmortem', {})
        module.exit_json(changed=False, post_mortem=post_mortem)
    except PagerDutyError as e:
        if e.status_code == 404:
            module.exit_json(changed=False, post_mortem={})
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
