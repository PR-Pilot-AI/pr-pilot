import pytest
from unittest.mock import patch, MagicMock
from engine.agents.integration_tools.sentry_tools import search_sentry_issues


@pytest.fixture
@patch('requests.get')
def mock_sentry_api(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = [
        {
            'title': 'Issue 1',
            'permalink': 'http://example.com/issue1',
            'status': 'unresolved',
            'firstSeen': '2023-01-01T00:00:00Z',
            'lastSeen': '2023-01-02T00:00:00Z',
            'count': 10,
            'userCount': 5
        },
        {
            'title': 'Issue 2',
            'permalink': 'http://example.com/issue2',
            'status': 'resolved',
            'firstSeen': '2023-01-03T00:00:00Z',
            'lastSeen': '2023-01-04T00:00:00Z',
            'count': 7,
            'userCount': 3
        }
    ]
    mock_get.return_value = mock_response
    return mock_get


def test_search_sentry_issues(mock_sentry_api):
    api_key = 'fake_api_key'
    query = 'is:unresolved'
    result = search_sentry_issues(api_key, query)
    assert "Found 2 issues matching the query" in result
    assert "Title: Issue 1" in result
    assert "Title: Issue 2" in result
