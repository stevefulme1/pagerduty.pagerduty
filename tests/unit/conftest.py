"""Shared fixtures for pagerduty.pagerduty unit tests."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import sys
import importlib
from unittest.mock import MagicMock

import pytest

# Build the ansible_collections namespace path so that
# ansible_collections.pagerduty.pagerduty resolves to the repo root.
COLLECTION_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# We need a parent dir that acts as ansible_collections/pagerduty/pagerduty -> COLLECTION_ROOT
_fake_root = os.path.join(COLLECTION_ROOT, '.test_namespace')
_ns_path = os.path.join(_fake_root, 'ansible_collections', 'pagerduty', 'pagerduty')

if not os.path.islink(_ns_path):
    os.makedirs(os.path.join(_fake_root, 'ansible_collections', 'pagerduty'), exist_ok=True)
    try:
        os.symlink(COLLECTION_ROOT, _ns_path)
    except OSError:
        pass

if _fake_root not in sys.path:
    sys.path.insert(0, _fake_root)

# Ensure the namespace packages are importable
for pkg in ('ansible_collections', 'ansible_collections.pagerduty'):
    if pkg not in sys.modules:
        mod = importlib.import_module(pkg) if pkg == 'ansible_collections' else None
        if mod is None:
            import types
            mod = types.ModuleType(pkg)
            mod.__path__ = [os.path.join(_fake_root, pkg.replace('.', os.sep))]
            mod.__package__ = pkg
            sys.modules[pkg] = mod


@pytest.fixture
def module_args():
    """Return base module args for PagerDuty modules."""
    return {
        'api_token': 'test-token',
        'api_url': 'https://api.pagerduty.com',
    }


@pytest.fixture
def mock_client():
    """Return a MagicMock of PagerDutyClient."""
    client = MagicMock()
    client.get.return_value = {}
    client.post.return_value = {}
    client.put.return_value = {}
    client.delete.return_value = None
    client.list_all.return_value = []
    client.find_by_name.return_value = None
    client.find_by_id.return_value = None
    return client
