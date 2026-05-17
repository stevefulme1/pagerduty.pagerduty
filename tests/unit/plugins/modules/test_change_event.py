"""Unit tests for pagerduty.pagerduty.change_event module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.change_event"


@pytest.fixture
def change_event_args(module_args):
    module_args.update({'routing_key': 'R0key', 'summary': 'Deploy v1.2', 'source': 'jenkins', 'custom_details': {}})
    return module_args


class TestCreate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_create_change_event(self, mock_ansible, mock_pd_cls, change_event_args, mock_client):
        mock_ansible.return_value.params = change_event_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        pd._diff.return_value = {}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'change_event': {'id': 'ID1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.change_event import main
        main()
        pd.ensure_present.assert_called_once()
        pd.exit.assert_called_once()


class TestUpdate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_update_change_event(self, mock_ansible, mock_pd_cls, change_event_args, mock_client):
        mock_ansible.return_value.params = change_event_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'change_event': {'id': 'ID1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.change_event import main
        main()
        pd.ensure_present.assert_called_once()


class TestCheckMode:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_check_mode_no_api_calls(self, mock_ansible, mock_pd_cls, change_event_args, mock_client):
        mock_ansible.return_value.params = change_event_args
        mock_ansible.return_value.check_mode = True
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = True
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        from ansible_collections.pagerduty.pagerduty.plugins.modules.change_event import main
        main()
        mock_client.post.assert_not_called()
        mock_client.put.assert_not_called()
        mock_client.delete.assert_not_called()


class TestIdempotent:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_idempotent_no_change(self, mock_ansible, mock_pd_cls, change_event_args, mock_client):
        mock_ansible.return_value.params = change_event_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': False, 'change_event': {'id': 'ID1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.change_event import main
        main()
        pd.ensure_present.assert_called_once()


class TestErrorHandling:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_api_error_handled(self, mock_ansible, mock_pd_cls, change_event_args, mock_client):
        mock_ansible.return_value.params = change_event_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import PagerDutyError
        pd.ensure_present.side_effect = PagerDutyError("API Error", status_code=401)

        from ansible_collections.pagerduty.pagerduty.plugins.modules.change_event import main
        main()
        pd.fail.assert_called()


class TestReturnValues:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_return_structure(self, mock_ansible, mock_pd_cls, change_event_args, mock_client):
        mock_ansible.return_value.params = change_event_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'change_event': {'id': 'ID1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.change_event import main
        main()
        pd.exit.assert_called_once()
