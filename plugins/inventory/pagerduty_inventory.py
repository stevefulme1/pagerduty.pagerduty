from __future__ import absolute_import, division, print_function
__metaclass__ = type

"""Dynamic inventory plugin."""

DOCUMENTATION = r"""
---
name: pagerduty_inventory
plugin_type: inventory
short_description: Dynamic inventory from PagerDuty
description:
    - Discovers hosts from PagerDuty API.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    host:
        description: API host.
        type: str
        required: true
        env:
            - name: PAGERDUTY_HOST
    api_key:
        description: API key.
        type: str
        env:
            - name: PAGERDUTY_API_KEY
"""

from ansible.plugins.inventory import BaseInventoryPlugin

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class InventoryModule(BaseInventoryPlugin):
    NAME = "stevefulme1.pagerduty.pagerduty_inventory"

    def verify_file(self, path):
        if super().verify_file(path):
            return path.endswith(("pagerduty_inventory.yml", "pagerduty_inventory.yaml"))
        return False

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path, cache)
        self._read_config_data(path)
        if not HAS_REQUESTS:
            raise Exception("requests required")
        host = self.get_option("host")
        api_key = self.get_option("api_key")
        self.inventory.add_group("pagerduty")
        try:
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            resp = requests.get(f"https://{host}/api/v1/hosts", headers=headers, timeout=30)
            resp.raise_for_status()
            for item in resp.json().get("data", []):
                hostname = item.get("name", item.get("id", ""))
                if hostname:
                    self.inventory.add_host(hostname, group="pagerduty")
        except Exception as e:
            self.display.warning(f"Discovery failed: {e}")
