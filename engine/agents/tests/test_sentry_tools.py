import pytest
from unittest.mock import patch, MagicMock
from engine.agents.integration_tools.sentry_tools import search_sentry_issues, get_sentry_events


@pytest.fixture
def mock_sentry_api():
    with patch("engine.agents.integration_tools.sentry_tools.SentryAPI") as MockSentryAPI:
        yield MockSentryAPI


def test_search_sentry_issues(mock_sentry_api):
    mock_instance = mock_sentry_api.return_value
    mock_instance.search_issues.return_value = [
        {
            "title": "Test Issue",
            "id": "12345",
            "permalink": "http://example.com/issue/12345",
            "status": "unresolved",
            "count": 10,
            "firstSeen": "2023-01-01T00:00:00Z",
            "lastSeen": "2023-01-02T00:00:00Z",
        }
    ]

    result = search_sentry_issues("test query", "fake_api_key")
    assert "Found 1 issues matching the query" in result
    assert "Test Issue" in result


def test_get_sentry_events(mock_sentry_api):
    mock_instance = mock_sentry_api.return_value
    mock_instance.get_events.return_value = [
        {
            "eventID": "abc123",
            "dateCreated": "2023-01-01T00:00:00Z",
            "message": "Test event message",
        }
    ]

    result = get_sentry_events("12345", "fake_api_key")
    assert "Found 1 events for issue ID" in result
    assert "Test event message" in result
