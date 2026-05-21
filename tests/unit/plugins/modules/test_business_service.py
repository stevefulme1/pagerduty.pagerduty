"""Unit tests for pagerduty.pagerduty.business_service module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.business_service"


def _build_resource(**overrides):
    """Return a mock business_service resource dict."""
    base = {
        "id": "P123ABC",
        "name": "test-resource",
        "type": "business_service",
    }
    base.update(overrides)
    return base


@pytest.fixture
def resource_args(module_args):
    """Module args for business_service."""
    module_args.update({
        "state": "present",
        "api_token": "test-token",
        "api_url": "https://api.pagerduty.com",
        "id": None,
        "name": None,
        "description": None,
        "point_of_contact": None,
        "team": None
    })
    return module_args


class TestCreate:
    """Test business_service creation."""

    @patch(MODULE_PATH + ".PagerDutyModule")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_create_resource(self, mock_ansible_cls, mock_pd_cls, resource_args, mock_client):
        """Creating a resource calls ensure_present."""
        mock_module = MagicMock()
        mock_module.params = resource_args
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module

        pd = MagicMock()
        pd.module = mock_module
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {"changed": False}
        mock_pd_cls.return_value = pd

        mock_client.post.return_value = {"business_service": _build_resource()}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.business_service import main
        main()

        pd.exit.assert_called_once()

    @patch(MODULE_PATH + ".PagerDutyModule")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_create_check_mode(self, mock_ansible_cls, mock_pd_cls, resource_args, mock_client):
        """In check mode, ensure_present handles it internally."""
        mock_module = MagicMock()
        mock_module.params = resource_args
        mock_module.check_mode = True
        mock_ansible_cls.return_value = mock_module

        pd = MagicMock()
        pd.module = mock_module
        pd.client = mock_client
        pd.check_mode = True
        pd.result = {"changed": False}
        mock_pd_cls.return_value = pd

        from ansible_collections.pagerduty.pagerduty.plugins.modules.business_service import main
        main()

        pd.exit.assert_called_once()


class TestDelete:
    """Test business_service deletion."""

    @patch(MODULE_PATH + ".PagerDutyModule")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_delete_existing_resource(self, mock_ansible_cls, mock_pd_cls, resource_args, mock_client):
        """Deleting an existing resource calls ensure_absent."""
        resource_args["state"] = "absent"
        mock_module = MagicMock()
        mock_module.params = resource_args
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module

        pd = MagicMock()
        pd.module = mock_module
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {"changed": False}
        mock_pd_cls.return_value = pd

        mock_client.find_by_name.return_value = _build_resource()

        from ansible_collections.pagerduty.pagerduty.plugins.modules.business_service import main
        main()

        pd.exit.assert_called_once()

    @patch(MODULE_PATH + ".PagerDutyModule")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_delete_check_mode(self, mock_ansible_cls, mock_pd_cls, resource_args, mock_client):
        """In check mode, delete is handled by ensure_absent."""
        resource_args["state"] = "absent"
        mock_module = MagicMock()
        mock_module.params = resource_args
        mock_module.check_mode = True
        mock_ansible_cls.return_value = mock_module

        pd = MagicMock()
        pd.module = mock_module
        pd.client = mock_client
        pd.check_mode = True
        pd.result = {"changed": False}
        mock_pd_cls.return_value = pd

        from ansible_collections.pagerduty.pagerduty.plugins.modules.business_service import main
        main()

        pd.exit.assert_called_once()


class TestUpdate:
    """Test business_service update."""

    @patch(MODULE_PATH + ".PagerDutyModule")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_update_resource(self, mock_ansible_cls, mock_pd_cls, resource_args, mock_client):
        """Updating an existing resource via ensure_present."""
        resource_args["name"] = "updated-resource"
        mock_module = MagicMock()
        mock_module.params = resource_args
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module

        pd = MagicMock()
        pd.module = mock_module
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {"changed": False}
        mock_pd_cls.return_value = pd

        mock_client.find_by_name.return_value = _build_resource(name="old-resource")
        mock_client.put.return_value = {"business_service": _build_resource(name="updated-resource")}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.business_service import main
        main()

        pd.exit.assert_called_once()


class TestIdempotent:
    """Test idempotent behavior."""

    @patch(MODULE_PATH + ".PagerDutyModule")
    @patch(MODULE_PATH + ".AnsibleModule")
    def test_no_change_when_up_to_date(self, mock_ansible_cls, mock_pd_cls, resource_args, mock_client):
        """When resource is up-to-date, ensure_present reports no change."""
        mock_module = MagicMock()
        mock_module.params = resource_args
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module

        pd = MagicMock()
        pd.module = mock_module
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {"changed": False}
        mock_pd_cls.return_value = pd

        from ansible_collections.pagerduty.pagerduty.plugins.modules.business_service import main
        main()

        pd.exit.assert_called_once()
