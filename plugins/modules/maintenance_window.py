#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Auto-generated
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: maintenance_window
short_description: Manage maintenance windows
version_added: "0.1.0"
description:
  - Create, update, and delete maintenance_window resources.
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

  maintenance_window:
    description:
      - >-
        Dictionary describing the maintenance window. Must include
        C(start_time), C(end_time), and C(services) list.
    type: dict

    required: true
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
- name: Create a maintenance window
  pagerduty.pagerduty.maintenance_window:
    maintenance_window:
      start_time: "2024-06-01T00:00:00Z"
      end_time: "2024-06-01T04:00:00Z"
      services:
        - id: PSVC123
          type: service_reference
    state: present

- name: Update a maintenance window
  pagerduty.pagerduty.maintenance_window:
    id: PMW123
    maintenance_window:
      start_time: "2024-06-01T00:00:00Z"
      end_time: "2024-06-01T06:00:00Z"
      services:
        - id: PSVC123
          type: service_reference
    state: present

- name: Delete a maintenance window
  pagerduty.pagerduty.maintenance_window:
    id: PMW123
    state: absent
"""

RETURN = r"""

maintenance_window:
  description: The maintenance window resource as returned by the PagerDuty API.
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
    """Retrieve the current state of the maintenance_window via GET."""
    identifier = module.params.get("id")
    if identifier is None:
        return None
    try:
        response = client.get("/maintenance_windows/{0}".format(identifier))
        if isinstance(response, dict):
            return response.get("maintenance_window", response)
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

    if module.params.get("maintenance_window") is not None:
        payload["maintenance_window"] = module.params["maintenance_window"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            id=dict(type="str", required=False),
            maintenance_window=dict(
                type="dict",

                required=True,

            ),

        )
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["id"])],
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
                        "/maintenance_windows",
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
                    path = "/maintenance_windows/{id}".replace(
                        "{id}", str(identifier)
                    )
                    response = client.put(
                        path,
                        data=desired,
                    )
                    result.update(response if isinstance(response, dict) else {})

            else:
                # Resource exists and is up-to-date

                result["maintenance_window"] = current.get("maintenance_window")

        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/maintenance_windows/{id}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
