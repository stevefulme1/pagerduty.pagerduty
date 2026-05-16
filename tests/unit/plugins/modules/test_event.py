"""Unit tests for pagerduty.pagerduty.event module."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch
import pytest

MODULE_PATH = "ansible_collections.pagerduty.pagerduty.plugins.modules.event"
EVENTS_CLIENT_PATH = MODULE_PATH.replace('.modules.event', '.module_utils.pagerduty.PagerDutyEventsClient')


@pytest.fixture
def event_args():
    return {
        'routing_key': 'test-routing-key',
        'event_action': 'trigger',
        'dedup_key': None,
        'summary': 'Disk usage above 90%',
        'source': 'web-server-01',
        'severity': 'critical',
        'component': None,
        'group': None,
        'class_type': None,
        'custom_details': None,
        'links': None,
        'images': None,
    }


class TestEventTrigger:
    @patch(MODULE_PATH + '.PagerDutyEventsClient')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_trigger_event(self, mock_ansible, mock_events_cls, event_args):
        mock_ansible.return_value.params = event_args
        mock_ansible.return_value.check_mode = False

        mock_client = MagicMock()
        mock_client.send_event.return_value = {
            'status': 'success', 'message': 'Event processed', 'dedup_key': 'dk123'
        }
        mock_events_cls.return_value = mock_client

        from ansible_collections.pagerduty.pagerduty.plugins.modules.event import main
        main()
        mock_client.send_event.assert_called_once()
        call_kwargs = mock_client.send_event.call_args[1]
        assert call_kwargs['event_action'] == 'trigger'
        assert call_kwargs['payload']['summary'] == 'Disk usage above 90%'


class TestEventAcknowledge:
    @patch(MODULE_PATH + '.PagerDutyEventsClient')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_acknowledge_event(self, mock_ansible, mock_events_cls, event_args):
        event_args['event_action'] = 'acknowledge'
        event_args['dedup_key'] = 'dk123'
        event_args['summary'] = None
        event_args['severity'] = None
        mock_ansible.return_value.params = event_args
        mock_ansible.return_value.check_mode = False

        mock_client = MagicMock()
        mock_client.send_event.return_value = {'status': 'success', 'message': 'Event processed', 'dedup_key': 'dk123'}
        mock_events_cls.return_value = mock_client

        from ansible_collections.pagerduty.pagerduty.plugins.modules.event import main
        main()
        call_kwargs = mock_client.send_event.call_args[1]
        assert call_kwargs['event_action'] == 'acknowledge'


class TestEventResolve:
    @patch(MODULE_PATH + '.PagerDutyEventsClient')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_resolve_event(self, mock_ansible, mock_events_cls, event_args):
        event_args['event_action'] = 'resolve'
        event_args['dedup_key'] = 'dk123'
        event_args['summary'] = None
        event_args['severity'] = None
        mock_ansible.return_value.params = event_args
        mock_ansible.return_value.check_mode = False

        mock_client = MagicMock()
        mock_client.send_event.return_value = {'status': 'success', 'message': 'Event processed', 'dedup_key': 'dk123'}
        mock_events_cls.return_value = mock_client

        from ansible_collections.pagerduty.pagerduty.plugins.modules.event import main
        main()
        call_kwargs = mock_client.send_event.call_args[1]
        assert call_kwargs['event_action'] == 'resolve'


class TestEventErrorHandling:
    @patch(MODULE_PATH + '.PagerDutyEventsClient')
    @patch(MODULE_PATH + '.AnsibleModule')
    def test_events_api_error(self, mock_ansible, mock_events_cls, event_args):
        from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import PagerDutyError
        mock_ansible.return_value.params = event_args
        mock_ansible.return_value.check_mode = False

        mock_client = MagicMock()
        mock_client.send_event.side_effect = PagerDutyError('Events API error: rate limited')
        mock_events_cls.return_value = mock_client

        from ansible_collections.pagerduty.pagerduty.plugins.modules.event import main
        main()
        mock_ansible.return_value.fail_json.assert_called_once()
        assert 'rate limited' in mock_ansible.return_value.fail_json.call_args[1]['msg']
