"""Unit tests for pagerduty.pagerduty.service_dependency module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.service_dependency"


@pytest.fixture
def service_dependency_args(module_args):
    module_args.update({'dependent_service': 'SVC1', 'supporting_service': 'SVC2', 'state': 'present'})
    return module_args


class TestCreate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_create_service_dependency(self, mock_ansible, mock_pd_cls, service_dependency_args, mock_client):
        mock_ansible.return_value.params = service_dependency_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        pd._diff.return_value = {}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'service_dependency': {'id': 'ID1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service_dependency import main
        main()
        pd.ensure_present.assert_called_once()
        pd.exit.assert_called_once()


class TestUpdate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_update_service_dependency(self, mock_ansible, mock_pd_cls, service_dependency_args, mock_client):
        mock_ansible.return_value.params = service_dependency_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'service_dependency': {'id': 'ID1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service_dependency import main
        main()
        pd.ensure_present.assert_called_once()


class TestDelete:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_delete_service_dependency(self, mock_ansible, mock_pd_cls, service_dependency_args, mock_client):
        service_dependency_args['state'] = 'absent'
        mock_ansible.return_value.params = service_dependency_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_absent.return_value = {'changed': True}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service_dependency import main
        main()
        pd.ensure_absent.assert_called_once()


class TestCheckMode:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_check_mode_no_api_calls(self, mock_ansible, mock_pd_cls, service_dependency_args, mock_client):
        mock_ansible.return_value.params = service_dependency_args
        mock_ansible.return_value.check_mode = True
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = True
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service_dependency import main
        main()
        mock_client.post.assert_not_called()
        mock_client.put.assert_not_called()
        mock_client.delete.assert_not_called()


class TestIdempotent:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_idempotent_no_change(self, mock_ansible, mock_pd_cls, service_dependency_args, mock_client):
        mock_ansible.return_value.params = service_dependency_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': False, 'service_dependency': {'id': 'ID1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service_dependency import main
        main()
        pd.ensure_present.assert_called_once()


class TestErrorHandling:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_api_error_handled(self, mock_ansible, mock_pd_cls, service_dependency_args, mock_client):
        mock_ansible.return_value.params = service_dependency_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import PagerDutyError
        pd.ensure_present.side_effect = PagerDutyError("API Error", status_code=401)

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service_dependency import main
        main()
        pd.fail.assert_called()


class TestReturnValues:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_return_structure(self, mock_ansible, mock_pd_cls, service_dependency_args, mock_client):
        mock_ansible.return_value.params = service_dependency_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'service_dependency': {'id': 'ID1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.service_dependency import main
        main()
        pd.exit.assert_called_once()
