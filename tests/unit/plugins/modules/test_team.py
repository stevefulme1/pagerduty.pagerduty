"""Unit tests for pagerduty.pagerduty.team module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.team"


@pytest.fixture
def team_args(module_args):
    module_args.update({
        'name': 'Engineering',
        'description': 'Engineering team',
        'parent': None,
        'state': 'present',
    })
    return module_args


class TestTeamCreate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_create_team(self, mock_ansible, mock_pd_cls, team_args, mock_client):
        mock_ansible.return_value.params = team_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'team': {'id': 'PTEAM1', 'name': 'Engineering'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.team import main
        main()
        pd.ensure_present.assert_called_once()
        pd.exit.assert_called_once()


class TestTeamDelete:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_delete_team(self, mock_ansible, mock_pd_cls, team_args, mock_client):
        team_args['state'] = 'absent'
        mock_ansible.return_value.params = team_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_absent.return_value = {'changed': True}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.team import main
        main()
        pd.ensure_absent.assert_called_once()


class TestTeamIdempotent:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_idempotent_no_changes(self, mock_ansible, mock_pd_cls, team_args, mock_client):
        mock_ansible.return_value.params = team_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        # ensure_present returns changed=False when no changes
        pd.ensure_present.return_value = {'changed': False, 'team': {'id': 'PTEAM1', 'name': 'Engineering'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.team import main
        main()
        mock_client.post.assert_not_called()
        mock_client.put.assert_not_called()
