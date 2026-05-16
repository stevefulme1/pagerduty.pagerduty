"""Unit tests for pagerduty.pagerduty shared module_utils."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from unittest.mock import MagicMock, patch

import pytest

MODULE_UTILS_PATH = "ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty"


@pytest.fixture
def client():
    from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import PagerDutyClient
    module = MagicMock()
    module.params = {'api_token': 'test-token', 'api_url': 'https://api.pagerduty.com'}
    return PagerDutyClient(module)


class TestHeaders:
    def test_headers_contain_auth_and_content_type(self, client):
        headers = client._headers()
        assert headers['Authorization'] == 'Token token=test-token'
        assert headers['Content-Type'] == 'application/json'
        assert 'Accept' in headers


class TestRequest:
    @patch(MODULE_UTILS_PATH + '.open_url')
    def test_successful_response(self, mock_open_url, client):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.read.return_value = json.dumps({'service': {'id': 'P1'}}).encode()
        mock_open_url.return_value = mock_resp

        result = client.request('GET', '/services/P1')
        assert result == {'service': {'id': 'P1'}}

    @patch(MODULE_UTILS_PATH + '.open_url')
    def test_error_response_raises_pagerduty_error(self, mock_open_url, client):
        from ansible_collections.pagerduty.pagerduty.plugins.module_utils.pagerduty import PagerDutyError
        error = Exception('API error')
        error.code = 400
        error.read = MagicMock(return_value=json.dumps({
            'error': {'message': 'Invalid Input', 'errors': ['name is required']}
        }).encode())
        mock_open_url.side_effect = error

        with pytest.raises(PagerDutyError, match='Invalid Input: name is required'):
            client.request('POST', '/services', data={'service': {}})


class TestListAll:
    @patch(MODULE_UTILS_PATH + '.open_url')
    def test_pagination(self, mock_open_url, client):
        page1 = MagicMock()
        page1.getcode.return_value = 200
        page1.read.return_value = json.dumps({
            'services': [{'id': 'P1'}], 'more': True
        }).encode()

        page2 = MagicMock()
        page2.getcode.return_value = 200
        page2.read.return_value = json.dumps({
            'services': [{'id': 'P2'}], 'more': False
        }).encode()

        mock_open_url.side_effect = [page1, page2]

        results = client.list_all('/services', 'services')
        assert len(results) == 2
        assert results[0]['id'] == 'P1'
        assert results[1]['id'] == 'P2'


class TestFindByName:
    @patch(MODULE_UTILS_PATH + '.open_url')
    def test_returns_matching_item(self, mock_open_url, client):
        resp = MagicMock()
        resp.getcode.return_value = 200
        resp.read.return_value = json.dumps({
            'services': [{'id': 'P1', 'name': 'Web'}, {'id': 'P2', 'name': 'API'}],
            'more': False
        }).encode()
        mock_open_url.return_value = resp

        result = client.find_by_name('/services', 'services', 'API')
        assert result['id'] == 'P2'


class TestFindById:
    @patch(MODULE_UTILS_PATH + '.open_url')
    def test_returns_none_on_404(self, mock_open_url, client):
        error = Exception('HTTP Error 404: Not Found')
        error.code = 404
        error.read = MagicMock(return_value=b'{"error":{"message":"Not Found"}}')
        mock_open_url.side_effect = error

        result = client.find_by_id('/services/PNOTFOUND', 'service')
        assert result is None
