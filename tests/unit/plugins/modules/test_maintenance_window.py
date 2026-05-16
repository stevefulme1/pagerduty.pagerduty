"""Unit tests for pagerduty.pagerduty.maintenance_window module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.maintenance_window"


@pytest.fixture
def mw_args(module_args):
    module_args.update({
        'id': None,
        'description': 'Scheduled deployment',
        'start_time': '2024-12-01T02:00:00Z',
        'end_time': '2024-12-01T04:00:00Z',
        'services': ['PSVC123'],
        'state': 'present',
    })
    return module_args


class TestMaintenanceWindowCreate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_create_maintenance_window(self, mock_ansible, mock_pd_cls, mw_args, mock_client):
        mock_ansible.return_value.params = mw_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        # No existing window found
        mock_client.list_all.return_value = []
        mock_client.post.return_value = {
            'maintenance_window': {'id': 'PMW1', 'description': 'Scheduled deployment'}
        }

        from ansible_collections.pagerduty.pagerduty.plugins.modules.maintenance_window import main
        main()
        pd.exit.assert_called_once()


class TestMaintenanceWindowDelete:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_delete_maintenance_window(self, mock_ansible, mock_pd_cls, mw_args, mock_client):
        mw_args['state'] = 'absent'
        mw_args['id'] = 'PMW1'
        mw_args['start_time'] = None
        mw_args['end_time'] = None
        mw_args['services'] = None
        mock_ansible.return_value.params = mw_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        mock_client.find_by_id.return_value = {'id': 'PMW1', 'description': 'Scheduled deployment'}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.maintenance_window import main
        main()
        pd.exit.assert_called_once()
