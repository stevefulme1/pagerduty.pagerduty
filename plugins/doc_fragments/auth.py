
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Auto-generated
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment:
    """Documentation fragment for stevefulme1.pagerduty authentication."""

    DOCUMENTATION = r"""
options:

  api_key:
    description:
      - The API key used to authenticate with the pagerduty API.

      - Sent as the C(X-API-Key) header.

      - Can also be set via the E(STEVEFULME1_PAGERDUTY_API_KEY) environment variable.
    type: str
    required: true

  api_url:
    description:
      - The base URL of the pagerduty API.
    type: str
    default: "https://api.pagerduty.com"
  validate_certs:
    description:
      - Whether to validate SSL/TLS certificates when connecting to the API.
    type: bool
    default: true
  request_timeout:
    description:
      - Timeout in seconds for API requests.
    type: int
    default: 30
"""
