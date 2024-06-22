import pytest
from unittest.mock import patch, MagicMock
from engine.agents.integration_tools.sentry_tools import fetch_sentry_event, fetch_sentry_issue


@pytest.fixture
@patch('engine.agents.integration_tools.sentry_tools.requests.get')
def mock_requests_get(mock_get):
    yield mock_get


def test_fetch_sentry_event(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'id': 'event1'}
    mock_requests_get.return_value = mock_response

    result = fetch_sentry_event('project1', 'event1', 'fake_api_key')
    assert result == {'id': 'event1'}
    mock_requests_get.assert_called_once_with(
        'https://sentry.io/api/0/projects/project1/events/event1/',
        headers={'Authorization': 'Bearer fake_api_key'}
    )


def test_fetch_sentry_event_error(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = 'Not Found'
    mock_requests_get.return_value = mock_response

    result = fetch_sentry_event('project1', 'event1', 'fake_api_key')
    assert 'Error fetching Sentry event' in result
    mock_requests_get.assert_called_once_with(
        'https://sentry.io/api/0/projects/project1/events/event1/',
        headers={'Authorization': 'Bearer fake_api_key'}
    )


def test_fetch_sentry_issue(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'id': 'issue1'}
    mock_requests_get.return_value = mock_response

    result = fetch_sentry_issue('project1', 'issue1', 'fake_api_key')
    assert result == {'id': 'issue1'}
    mock_requests_get.assert_called_once_with(
        'https://sentry.io/api/0/projects/project1/issues/issue1/',
        headers={'Authorization': 'Bearer fake_api_key'}
    )


def test_fetch_sentry_issue_error(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = 'Not Found'
    mock_requests_get.return_value = mock_response

    result = fetch_sentry_issue('project1', 'issue1', 'fake_api_key')
    assert 'Error fetching Sentry issue' in result
    mock_requests_get.assert_called_once_with(
        'https://sentry.io/api/0/projects/project1/issues/issue1/',
        headers={'Authorization': 'Bearer fake_api_key'}
    )
