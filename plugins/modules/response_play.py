#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: response_play
short_description: Manage PagerDuty response plays
description:
  - Create, update, and delete response plays in PagerDuty.
  - Response plays automate incident response actions.
version_added: "1.0.0"
author: Ansible PagerDuty Collection Authors (@ansible-collections)
options:
  name:
    description: The name of the response play.
    type: str
    required: true
  description:
    description: A description of the response play.
    type: str
    default: ''
  team:
    description: The team name or ID that owns the response play.
    type: str
  responders:
    description:
      - List of responders to add when the play is run.
      - Each responder is a dict with type (escalation_policy or user) and id.
    type: list
    elements: dict
    default: []
  runnability:
    description: Who can run this response play.
    type: str
    choices: [services, teams]
    default: services
  conference_number:
    description: Phone number for the conference bridge.
    type: str
  conference_url:
    description: URL for the conference bridge.
    type: str
  from_email:
    description: The email address of the user making the request. Required by PagerDuty API.
    type: str
    required: true
  state:
    description: Whether the response play should exist or not.
    type: str
    default: present
    choices: [present, absent]
extends_documentation_fragment:
  - pagerduty.pagerduty.pagerduty
'''

EXAMPLES = r'''
- name: Create a response play
  pagerduty.pagerduty.response_play:
    api_token: "{{ pd_token }}"
    name: "Major Incident Response"
    description: "Mobilize the incident team"
    from_email: "admin@example.com"
    responders:
      - type: escalation_policy
        id: PXXXXXX
      - type: user
        id: PYYYYYY
    runnability: services
    conference_number: "+1-555-555-0100"
    conference_url: "https://meet.example.com/incident"
    state: present

- name: Delete a response play
  pagerduty.pagerduty.response_play:
    api_token: "{{ pd_token }}"
    name: "Old Response Play"
    from_email: "admin@example.com"
    state: absent
'''

RETURN = r'''
response_play:
  description: The response play object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import (
    PAGERDUTY_COMMON_ARGS, PagerDutyModule, PagerDutyError
)


def find_response_play(pd, name):
    """Find a response play by name."""
    try:
        plays = pd.client.list_all('/response_plays', 'response_plays')
    except PagerDutyError:
        return None
    for play in plays:
        if play.get('name') == name:
            return play
    return None


def build_payload(module):
    """Build the response play payload."""
    responder_refs = []
    for r in module.params['responders']:
        ref_type = '{0}_reference'.format(r['type'])
        responder_refs.append({'type': ref_type, 'id': r['id']})

    data = {
        'name': module.params['name'],
        'description': module.params['description'],
        'responders': responder_refs,
        'runnability': module.params['runnability'],
        'type': 'response_play',
    }
    if module.params['team']:
        data['team'] = {'id': module.params['team'], 'type': 'team_reference'}
    if module.params['conference_number'] or module.params['conference_url']:
        data['conference_bridge'] = {}
        if module.params['conference_number']:
            data['conference_bridge']['conference_number'] = module.params['conference_number']
        if module.params['conference_url']:
            data['conference_bridge']['conference_url'] = module.params['conference_url']
    return data


def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
        team=dict(type='str'),
        responders=dict(type='list', elements='dict', default=[]),
        runnability=dict(type='str', default='services', choices=['services', 'teams']),
        conference_number=dict(type='str'),
        conference_url=dict(type='str'),
        from_email=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        **PAGERDUTY_COMMON_ARGS,
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    pd = PagerDutyModule(module)
    state = module.params['state']

    try:
        existing = find_response_play(pd, module.params['name'])

        if state == 'present':
            payload = build_payload(module)
            if existing:
                if not pd.check_mode:
                    result = pd.client.put(
                        '/response_plays/{0}'.format(existing['id']),
                        {'response_play': payload},
                    )
                    pd.result['response_play'] = result.get('response_play', result)
                else:
                    pd.result['response_play'] = existing
                pd.result['changed'] = True
            else:
                if not pd.check_mode:
                    result = pd.client.post('/response_plays', {'response_play': payload})
                    pd.result['response_play'] = result.get('response_play', result)
                pd.result['changed'] = True
        else:
            if existing:
                if not pd.check_mode:
                    pd.client.delete('/response_plays/{0}'.format(existing['id']))
                pd.result['changed'] = True

        pd.exit()
    except PagerDutyError as e:
        pd.fail('PagerDuty API error: {0}'.format(str(e)))


if __name__ == '__main__':
    main()
