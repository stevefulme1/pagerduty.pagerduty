#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Auto-generated
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: webhook_subscription
short_description: Manage webhooks
version_added: "0.1.0"
description:
  - Create, update, and delete webhook_subscription resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulme1)"
options:
  id:
    description:
      - The PagerDuty resource ID. Required when C(state=absent).
    type: str
    required: false
    version_added: "0.1.0"

  state:
    description:
      - Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
    version_added: "0.1.0"

  webhook_subscription:
    description:
      - >-
        Dictionary describing the webhook subscription. Must include
        C(delivery_method) and C(events) list.
    type: dict
    version_added: "0.1.0"


extends_documentation_fragment:
  - pagerduty.pagerduty.auth
"""

EXAMPLES = r"""
- name: Create a webhook subscription
  pagerduty.pagerduty.webhook_subscription:
    webhook_subscription:
      delivery_method:
        type: http_delivery_method
        url: https://example.com/webhooks/pagerduty
      events:
        - incident.triggered
        - incident.resolved
      filter:
        type: account_reference
    state: present

- name: Update a webhook subscription
  pagerduty.pagerduty.webhook_subscription:
    id: PWEBHOOK123
    webhook_subscription:
      delivery_method:
        type: http_delivery_method
        url: https://example.com/webhooks/pagerduty-v2
      events:
        - incident.triggered
        - incident.acknowledged
        - incident.resolved
    state: present

- name: Delete a webhook subscription
  pagerduty.pagerduty.webhook_subscription:
    id: PWEBHOOK123
    state: absent
"""

RETURN = r"""

webhook_subscription:
  description: The webhook subscription resource as returned by the PagerDuty API.
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
    """Retrieve the current state of the webhook_subscription via GET."""
    identifier = module.params.get("id")
    if identifier is None:
        return None
    try:
        response = client.get("/webhook_subscriptions/{0}".format(identifier))
        if isinstance(response, dict):
            return response.get("webhook_subscription", response)
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

    if module.params.get("webhook_subscription") is not None:
        payload["webhook_subscription"] = module.params["webhook_subscription"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            id=dict(type="str", required=False),
            state=dict(type="str", choices=["present", "absent"], default="present"),

            webhook_subscription=dict(
                type="dict",

            ),

        )
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
        required_if=[("state", "present", ["webhook_subscription"]), ("state", "absent", ["id"])],
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
                        "/webhook_subscriptions",
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
                    path = "/webhook_subscriptions/{id}".replace(
                        "{id}", str(identifier)
                    )
                    response = client.put(
                        path,
                        data=desired,
                    )
                    result.update(response if isinstance(response, dict) else {})

            else:
                # Resource exists and is up-to-date

                result["webhook_subscription"] = current.get("webhook_subscription")

        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/webhook_subscriptions/{id}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
