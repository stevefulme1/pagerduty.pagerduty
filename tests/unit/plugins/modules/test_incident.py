"""Unit tests for pagerduty.pagerduty.incident module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.incident"


@pytest.fixture
def incident_args(module_args):
    module_args.update({
        'id': None,
        'title': 'Server outage',
        'service': 'PSVC123',
        'urgency': 'high',
        'body': None,
        'escalation_policy': None,
        'priority': None,
        'incident_key': None,
        'status': None,
        'assignments': None,
        'state': 'present',
    })
    return module_args


class TestIncidentCreate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_create_incident(self, mock_ansible, mock_pd_cls, incident_args, mock_client):
        mock_ansible.return_value.params = incident_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        mock_client.post.return_value = {'incident': {'id': 'PINC1', 'title': 'Server outage'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.incident import main
        main()
        pd.exit.assert_called_once()


class TestIncidentResolve:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_resolve_incident(self, mock_ansible, mock_pd_cls, incident_args, mock_client):
        incident_args['state'] = 'absent'
        incident_args['id'] = 'PINC1'
        incident_args['title'] = None
        mock_ansible.return_value.params = incident_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        mock_client.find_by_id.return_value = {'id': 'PINC1', 'status': 'triggered'}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.incident import main
        main()
        pd.exit.assert_called_once()


class TestIncidentUpdateStatus:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_update_status(self, mock_ansible, mock_pd_cls, incident_args, mock_client):
        incident_args['id'] = 'PINC1'
        incident_args['status'] = 'acknowledged'
        incident_args['title'] = None
        mock_ansible.return_value.params = incident_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        mock_client.find_by_id.return_value = {'id': 'PINC1', 'status': 'triggered'}
        mock_client.put.return_value = {'incident': {'id': 'PINC1', 'status': 'acknowledged'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.incident import main
        main()
        pd.exit.assert_called_once()
