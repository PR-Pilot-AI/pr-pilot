import pytest
from unittest.mock import patch, MagicMock
from engine.agents.integration_tools.sentry_tools import fetch_sentry_event, fetch_sentry_issue


@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get


def test_fetch_sentry_event_success(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'event': 'details'}
    mock_requests_get.return_value = mock_response

    result = fetch_sentry_event('event_id', 'api_key')
    assert result == {'event': 'details'}


def test_fetch_sentry_event_failure(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = 'Not Found'
    mock_requests_get.return_value = mock_response

    result = fetch_sentry_event('event_id', 'api_key')
    assert result == 'Error fetching Sentry event: 404'


def test_fetch_sentry_issue_success(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'issue': 'details'}
    mock_requests_get.return_value = mock_response

    result = fetch_sentry_issue('issue_id', 'api_key')
    assert result == {'issue': 'details'}


def test_fetch_sentry_issue_failure(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = 'Not Found'
    mock_requests_get.return_value = mock_response

    result = fetch_sentry_issue('issue_id', 'api_key')
    assert result == 'Error fetching Sentry issue: 404'
