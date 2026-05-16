"""Unit tests for pagerduty.pagerduty.escalation_policy module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.escalation_policy"


@pytest.fixture
def ep_args(module_args):
    module_args.update({
        'name': 'Engineering On-Call',
        'description': 'Primary escalation',
        'num_loops': 2,
        'on_call_handoff_notifications': None,
        'rules': [
            {'escalation_delay_in_minutes': 30, 'targets': [{'type': 'user_reference', 'id': 'PUSR1'}]}
        ],
        'state': 'present',
    })
    return module_args


class TestEscalationPolicyCreate:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_create_with_rules(self, mock_ansible, mock_pd_cls, ep_args, mock_client):
        mock_ansible.return_value.params = ep_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': True, 'escalation_policy': {'id': 'PEP1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.escalation_policy import main
        main()
        pd.ensure_present.assert_called_once()
        call_kwargs = pd.ensure_present.call_args
        assert call_kwargs[1]['resource_key'] == 'escalation_policy'


class TestEscalationPolicyDelete:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_delete(self, mock_ansible, mock_pd_cls, ep_args, mock_client):
        ep_args['state'] = 'absent'
        mock_ansible.return_value.params = ep_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        from ansible_collections.pagerduty.pagerduty.plugins.modules.escalation_policy import main
        main()
        pd.ensure_absent.assert_called_once()


class TestEscalationPolicyIdempotent:
    @patch(MODULE_PATH + '.PagerDutyModule')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_idempotent(self, mock_ansible, mock_pd_cls, ep_args, mock_client):
        mock_ansible.return_value.params = ep_args
        mock_ansible.return_value.check_mode = False
        pd = MagicMock()
        pd.module = mock_ansible.return_value
        pd.client = mock_client
        pd.check_mode = False
        pd.result = {'changed': False}
        mock_pd_cls.return_value = pd

        pd.ensure_present.return_value = {'changed': False, 'escalation_policy': {'id': 'PEP1'}}

        from ansible_collections.pagerduty.pagerduty.plugins.modules.escalation_policy import main
        main()
        mock_client.post.assert_not_called()
        mock_client.put.assert_not_called()
