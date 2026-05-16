"""Unit tests for pagerduty.pagerduty.service module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.service"


@pytest.fixture
def service_args(module_args):
    module_args.update({
        'name': 'Web App',
        'description': 'Production web app',
        'escalation_policy': 'POLICY1',
        'alert_creation': 'create_alerts_and_incidents',
        'alert_grouping_parameters': None,
        'auto_resolve_timeout': None,
        'acknowledgement_timeout': None,
        'status': None,
        'state': 'present',
    })
    return module_args


class TestServiceCreate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_create_service(self, mock_ansible, mock_pd_cls, service_args, mock_client):
        mock_ansible.return_value.params = service_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        pd._diff.return_value = {}
        mock_pd_cls.return_value = pd

        # Service not found -> create
        pd.ensure_present.return_value = {'changed': True, 'service': {'id': 'PSVC1', 'name': 'Web App'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service import main
        main()
        pd.ensure_present.assert_called_once()
        pd.exit.assert_called_once()


class TestServiceUpdate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_update_service(self, mock_ansible, mock_pd_cls, service_args, mock_client):
        service_args['description'] = 'Updated description'
        mock_ansible.return_value.params = service_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'service': {'id': 'PSVC1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service import main
        main()
        pd.ensure_present.assert_called_once()


class TestServiceDelete:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_delete_service(self, mock_ansible, mock_pd_cls, service_args, mock_client):
        service_args['state'] = 'absent'
        mock_ansible.return_value.params = service_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_absent.return_value = {'changed': True}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service import main
        main()
        pd.ensure_absent.assert_called_once()


class TestServiceCheckMode:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_check_mode_no_api_calls(self, mock_ansible, mock_pd_cls, service_args, mock_client):
        mock_ansible.return_value.params = service_args
        mock_ansible.return_value.check_mode = True
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = True
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service import main
        main()
        mock_client.post.assert_not_called()
        mock_client.put.assert_not_called()
        mock_client.delete.assert_not_called()
