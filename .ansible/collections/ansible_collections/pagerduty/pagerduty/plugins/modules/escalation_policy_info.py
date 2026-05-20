#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Auto-generated
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: escalation_policy_info
short_description: Retrieve information about escalation_policy resources
version_added: "1.0.0"
description:
  - Retrieve a single escalation_policy by its identifier, or list all escalation_policy resources.
  - This module always reports C(changed=False).
author:
  - "Steve Fulmer (@stevefulme1)"
options:
  id:
    description:
      - The unique identifier of the escalation_policy to retrieve.
      - When omitted, all escalation_policy resources are listed.
    type: str
    required: false




  page:
    description:
      - Page number for paginated results.
      - Only applies when listing resources.
    type: int
    required: false
  page_size:
    description:
      - Number of results per page.
      - Only applies when listing resources.
    type: int
    required: false
extends_documentation_fragment:
  - pagerduty.pagerduty.auth
"""

EXAMPLES = r"""
- name: Get a specific escalation_policy
  pagerduty.pagerduty.escalation_policy_info:
    id: "example_id"
  register: result

- name: List all escalation_policy resources
  pagerduty.pagerduty.escalation_policy_info:
  register: result



- name: List escalation_policy resources with pagination
  pagerduty.pagerduty.escalation_policy_info:
    page: 1
    page_size: 50
  register: result
"""

RETURN = r"""
escalation_policys:
  description: List of escalation_policy resources matching the query.
  returned: always
  type: list
  elements: dict
  contains:

    escalation_policy:
      description: >-
        
      type: dict


"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.pagerduty.pagerduty.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def fetch_single(client, identifier):
    """Retrieve a single escalation_policy by identifier."""

    # No single-resource GET endpoint; filter from list
    items = client.get("/escalation_policies")
    if isinstance(items, dict):
        items = items.get("results", items.get("data", items.get("items", [])))
    for item in items:
        if str(item.get("id")) == str(identifier):
            return item
    return None



def fetch_list(client, module):
    """List escalation_policy resources with optional filtering and pagination."""

    params = {}







    page = module.params.get("page")
    page_size = module.params.get("page_size")

    if page is not None or page_size is not None:
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        response = client.get("/escalation_policies", params=params)
        if isinstance(response, dict):
            return response.get("results", response.get("data", response.get("items", [])))
        return response if isinstance(response, list) else []
    else:
        return client.get_paginated("/escalation_policies", params=params)



def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            id=dict(type="str", required=False),




            page=dict(type="int", required=False),
            page_size=dict(type="int", required=False),
        )
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ("id", "page"),
            ("id", "page_size"),
        ],
    )

    result = dict(
        changed=False,
        escalation_policys=[],
    )

    try:
        client = Client(module)
        identifier = module.params.get("id")

        if identifier is not None:
            item = fetch_single(client, identifier)
            result["escalation_policys"] = [item] if item else []
        else:
            result["escalation_policys"] = fetch_list(client, module)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
