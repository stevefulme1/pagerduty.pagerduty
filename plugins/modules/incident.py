#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Auto-generated
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: incident
short_description: Manage incidents
version_added: "0.1.0"
description:
  - Create, update, and delete incident resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulme1)"
options:
  state:
    description:
      - Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
    version_added: "0.1.0"

  incident:
    description:
      - >-
        Dictionary describing the incident. Must include C(type),
        C(title), and C(service) reference.
    type: dict
    version_added: "0.1.0"

  id:
    description:
      - The PagerDuty resource ID. Required when C(state=absent).
    type: str
    required: false
    version_added: "0.1.0"

extends_documentation_fragment:
  - pagerduty.pagerduty.auth
"""

EXAMPLES = r"""
- name: Create an incident
  pagerduty.pagerduty.incident:
    incident:
      type: incident
      title: Server on fire
      service:
        id: PSVC123
        type: service_reference
    state: present

- name: Update an incident
  pagerduty.pagerduty.incident:
    id: PINC123
    incident:
      type: incident_reference
      title: Server on fire - updated
      service:
        id: PSVC123
        type: service_reference
    state: present

- name: Resolve an incident
  pagerduty.pagerduty.incident:
    id: PINC123
    state: absent
"""

RETURN = r"""

incident:
  description: The incident resource as returned by the PagerDuty API.
  returned: success
  type: dict

"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def get_current_state(client, module):
    """Retrieve the current state of the incident via GET."""
    identifier = module.params.get("id")
    if identifier is None:
        return None
    try:
        response = client.get("/incidents/{0}".format(identifier))
        if isinstance(response, dict):
            return response.get("incident", response)
        return response
    except ClientError as e:
        if e.status_code == 404:
            return None
        raise


def needs_update(current, desired):
    """Compare current state against desired params and return True if an update is needed."""
    if current is None:
        return True
    for key, value in desired.items():
        if value is None:
            continue
        current_value = current.get(key)
        if current_value != value:
            return True
    return False


def build_payload(module):
    """Build the API request payload from module params."""
    payload = {}

    if module.params.get("incident") is not None:
        payload["incident"] = module.params["incident"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            id=dict(type="str", required=False),
            incident=dict(
                type="dict",

            ),

        )
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
        required_if=[("state", "present", ["incident"]), ("state", "absent", ["id"])],
    )

    state = module.params["state"]
    result = dict(changed=False, diff=dict(before={}, after={}))

    try:
        client = Client(module)
        current = get_current_state(client, module)

        if state == "present":
            desired = build_payload(module)

            if current is None:
                # Resource does not exist — create it
                result["changed"] = True
                result["diff"]["before"] = {}
                result["diff"]["after"] = desired

                if not module.check_mode:

                    response = client.post(
                        "/incidents",
                        data=desired,
                    )
                    result.update(response if isinstance(response, dict) else {})

            elif needs_update(current, desired):
                # Resource exists but needs updating
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = dict(current, **{k: v for k, v in desired.items() if v is not None})

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/incidents/{id}".replace(
                        "{id}", str(identifier)
                    )
                    response = client.put(
                        path,
                        data=desired,
                    )
                    result.update(response if isinstance(response, dict) else {})

            else:
                # Resource exists and is up-to-date

                result["incident"] = current.get("incident")

        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:
                    # PagerDuty incidents cannot be deleted; resolve instead
                    identifier = current.get("id")
                    path = "/incidents/{0}".format(identifier)
                    response = client.put(
                        path,
                        data={"incident": {"type": "incident_reference", "status": "resolved"}},
                    )
                    result.update(response if isinstance(response, dict) else {})

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
