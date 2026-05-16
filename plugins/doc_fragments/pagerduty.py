# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
  api_token:
    description:
      - PagerDuty REST API token.
      - Can also be set via the C(PAGERDUTY_API_TOKEN) or C(PD_API_TOKEN) environment variables.
    type: str
    required: true
  api_url:
    description:
      - PagerDuty API base URL.
    type: str
    default: https://api.pagerduty.com
'''
