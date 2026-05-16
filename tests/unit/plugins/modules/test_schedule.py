"""Unit tests for pagerduty.pagerduty.schedule module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.schedule"


@pytest.fixture
def schedule_args(module_args):
    module_args.update({
        'name': 'Primary On-Call',
        'description': None,
        'time_zone': 'America/New_York',
        'schedule_layers': [
            {
                'rotation_virtual_start': '2024-01-01T00:00:00-05:00',
                'rotation_turn_length_seconds': 604800,
                'start': '2024-01-01T00:00:00-05:00',
                'users': [{'user': {'type': 'user_reference', 'id': 'PUSR1'}}],
            }
        ],
        'state': 'present',
    })
    return module_args


class TestScheduleCreate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_create_schedule(self, mock_ansible, mock_pd_cls, schedule_args, mock_client):
        mock_ansible.return_value.params = schedule_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'schedule': {'id': 'PSCHED1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.schedule import main
        main()
        pd.ensure_present.assert_called_once()
        call_kwargs = pd.ensure_present.call_args
        assert call_kwargs[1]['resource_key'] == 'schedule'
        pd.exit.assert_called_once()


class TestScheduleDelete:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_delete_schedule(self, mock_ansible, mock_pd_cls, schedule_args, mock_client):
        schedule_args['state'] = 'absent'
        mock_ansible.return_value.params = schedule_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_absent.return_value = {'changed': True}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.schedule import main
        main()
        pd.ensure_absent.assert_called_once()
        pd.exit.assert_called_once()
