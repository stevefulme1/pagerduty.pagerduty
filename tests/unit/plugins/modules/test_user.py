"""Unit tests for pagerduty.pagerduty.user module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.user"


@pytest.fixture
def user_args(module_args):
    module_args.update({
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'role': 'user',
        'time_zone': None,
        'color': None,
        'description': None,
        'job_title': None,
        'state': 'present',
    })
    return module_args


class TestUserCreate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_create_user(self, mock_ansible, mock_pd_cls, user_args, mock_client):
        mock_ansible.return_value.params = user_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        pd._diff.return_value = {}
        mock_pd_cls.return_value = pd

        # No existing user found
        mock_client.list_all.return_value = []
        mock_client.post.return_value = {'user': {'id': 'PUSR1', 'name': 'Jane Doe', 'email': 'jane@example.com'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.user import main
        main()
        pd.exit.assert_called_once()


class TestUserFindByEmail:
    def test_find_user_by_email(self, mock_client):
        from ansible_collections.pagerduty.pagerduty.plugins.modules.user import find_user_by_email
        mock_client.list_all.return_value = [
            {'id': 'P1', 'email': 'bob@example.com'},
            {'id': 'P2', 'email': 'jane@example.com'},
        ]
        pd = MagicMock()
        pd.client = mock_client

        result = find_user_by_email(pd, 'jane@example.com')
        assert result['id'] == 'P2'

    def test_find_user_by_email_not_found(self, mock_client):
        from ansible_collections.pagerduty.pagerduty.plugins.modules.user import find_user_by_email
        mock_client.list_all.return_value = []
        pd = MagicMock()
        pd.client = mock_client

        result = find_user_by_email(pd, 'nobody@example.com')
        assert result is None


class TestUserDelete:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_delete_user(self, mock_ansible, mock_pd_cls, user_args, mock_client):
        user_args['state'] = 'absent'
        mock_ansible.return_value.params = user_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        # Simulate existing user found by email
        mock_client.list_all.return_value = [{'id': 'PUSR1', 'email': 'jane@example.com'}]

        from ansible_collections.pagerduty.pagerduty.plugins.modules.user import main
        main()
        pd.exit.assert_called_once()


class TestUserCheckMode:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_check_mode(self, mock_ansible, mock_pd_cls, user_args, mock_client):
        mock_ansible.return_value.params = user_args
        mock_ansible.return_value.check_mode = True
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = True
        pd.result = {'changed': False}
        pd._diff.return_value = {}
        mock_pd_cls.return_value = pd

        mock_client.list_all.return_value = []

        from ansible_collections.pagerduty.pagerduty.plugins.modules.user import main
        main()
        mock_client.post.assert_not_called()
        mock_client.put.assert_not_called()
