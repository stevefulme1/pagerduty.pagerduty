#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Auto-generated
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: maintenance_window_info
short_description: Retrieve information about maintenance_window resources
version_added: "0.1.0"
description:
  - Retrieve a single maintenance_window by its identifier, or list all maintenance_window resources.
  - This module always reports C(changed=False).
author:
  - "Steve Fulmer (@stevefulme1)"
options:
  id:
    description:
      - The unique identifier of the maintenance_window to retrieve.
      - When omitted, all maintenance_window resources are listed.
    type: str
    required: false

  offset:
    description:
      - Offset for paginated results.
      - Only applies when listing resources.
    type: int
    required: false
  limit:
    description:
      - Maximum number of results per request.
      - Only applies when listing resources.
    type: int
    required: false
extends_documentation_fragment:
  - pagerduty.pagerduty.auth
"""

EXAMPLES = r"""
- name: Get a specific maintenance_window
  pagerduty.pagerduty.maintenance_window_info:
    id: "example_id"
  register: result

- name: List all maintenance_window resources
  pagerduty.pagerduty.maintenance_window_info:
  register: result

- name: List maintenance_window resources with pagination
  pagerduty.pagerduty.maintenance_window_info:
    offset: 0
    limit: 50
  register: result
"""

RETURN = r"""
maintenance_windows:
  description: List of maintenance_window resources matching the query.
  returned: always
  type: list
  elements: dict
  contains:

    maintenance_window:
      description: >-
        A single maintenance_window resource returned by the PagerDuty API.
      type: dict


"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def fetch_single(client, identifier):
    """Retrieve a single maintenance_window by identifier."""

    try:
        response = client.get("/maintenance_windows/{0}".format(identifier))
        if isinstance(response, dict):
            return response.get("maintenance_window", response)
        return response
    except ClientError as e:
        if e.status_code == 404:
            return None
        raise


def fetch_list(client, module):
    """List maintenance_window resources with optional filtering and pagination."""

    params = {}

    offset = module.params.get("offset")
    limit = module.params.get("limit")

    if offset is not None or limit is not None:
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        response = client.get("/maintenance_windows", params=params)
        if isinstance(response, dict):
            return response.get("maintenance_windows", response.get("data", response.get("items", [])))
        return response if isinstance(response, list) else []
    else:
        return client.get_paginated("/maintenance_windows", params=params)


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            id=dict(type="str", required=False),

            offset=dict(type="int", required=False),
            limit=dict(type="int", required=False),
        )
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ("id", "offset"),
            ("id", "limit"),
        ],
    )

    result = dict(
        changed=False,
        maintenance_windows=[],
    )

    try:
        client = Client(module)
        identifier = module.params.get("id")

        if identifier is not None:
            item = fetch_single(client, identifier)
            result["maintenance_windows"] = [item] if item else []
        else:
            result["maintenance_windows"] = fetch_list(client, module)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
