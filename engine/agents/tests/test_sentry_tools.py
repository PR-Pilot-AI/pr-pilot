import pytest
from unittest.mock import patch, MagicMock
from engine.agents.integration_tools.sentry_tools import search_sentry_issues


@pytest.fixture
@patch('requests.get')
def mock_requests_get(mock_get):
    yield mock_get


def test_search_sentry_issues_success(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            'title': 'Issue 1',
            'permalink': 'http://example.com/issue1',
            'status': 'unresolved'
        },
        {
            'title': 'Issue 2',
            'permalink': 'http://example.com/issue2',
            'status': 'resolved'
        }
    ]
    mock_requests_get.return_value = mock_response

    result = search_sentry_issues('fake_api_key', 'query')
    assert "Found 2 issues matching the query 'query'" in result
    assert "Issue: Issue 1" in result
    assert "Issue: Issue 2" in result


def test_search_sentry_issues_no_results(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_requests_get.return_value = mock_response

    result = search_sentry_issues('fake_api_key', 'query')
    assert "No issues found matching the query 'query'" in result


def test_search_sentry_issues_error(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {'detail': 'Internal Server Error'}
    mock_requests_get.return_value = mock_response

    result = search_sentry_issues('fake_api_key', 'query')
    assert "Error searching Sentry issues" in result
