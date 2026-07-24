#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Auto-generated
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: incident_info
short_description: Retrieve information about incident resources
version_added: "0.1.0"
description:
  - Retrieve a single incident by its identifier, or list all incident resources.
  - This module always reports C(changed=False).
author:
  - "Steve Fulmer (@stevefulme1)"
options:
  id:
    description:
      - The unique identifier of the incident to retrieve.
      - When omitted, all incident resources are listed.
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
- name: Get a specific incident
  pagerduty.pagerduty.incident_info:
    id: "example_id"
  register: result

- name: List all incident resources
  pagerduty.pagerduty.incident_info:
  register: result

- name: List incident resources with pagination
  pagerduty.pagerduty.incident_info:
    offset: 0
    limit: 50
  register: result
"""

RETURN = r"""
incidents:
  description: List of incident resources matching the query.
  returned: always
  type: list
  elements: dict
  contains:

    incident:
      description: >-
        A single incident resource returned by the PagerDuty API.
      type: dict

"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def fetch_single(client, identifier):
    """Retrieve a single incident by identifier."""

    try:
        response = client.get("/incidents/{0}".format(identifier))
        if isinstance(response, dict):
            return response.get("incident", response)
        return response
    except ClientError as e:
        if e.status_code == 404:
            return None
        raise


def fetch_list(client, module):
    """List incident resources with optional filtering and pagination."""

    params = {}

    offset = module.params.get("offset")
    limit = module.params.get("limit")

    if offset is not None or limit is not None:
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        response = client.get("/incidents", params=params)
        if isinstance(response, dict):
            return response.get("incidents", response.get("data", response.get("items", [])))
        return response if isinstance(response, list) else []
    else:
        return client.get_paginated("/incidents", params=params)


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
        incidents=[],
    )

    try:
        client = Client(module)
        identifier = module.params.get("id")

        if identifier is not None:
            item = fetch_single(client, identifier)
            result["incidents"] = [item] if item else []
        else:
            result["incidents"] = fetch_list(client, module)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
