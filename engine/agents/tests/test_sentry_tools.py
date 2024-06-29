from unittest.mock import patch

import pytest

from engine.agents.integration_tools.sentry_tools import (
    search_sentry_issues,
    get_sentry_events,
)


@pytest.fixture(autouse=True)
def mock_task_event():
    with patch("engine.agents.integration_tools.sentry_tools.TaskEvent") as mock:
        yield mock


@pytest.fixture
def mock_sentry_api():
    with patch(
        "engine.agents.integration_tools.sentry_tools.SentryAPI"
    ) as MockSentryAPI:
        yield MockSentryAPI


@pytest.mark.django_db
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

    result = search_sentry_issues(
        "test query", "fake_api_key", "fake_org", "fake_project"
    )
    assert "Found 1 issues matching the query" in result
    assert "Test Issue" in result


@pytest.mark.django_db
def test_get_sentry_events(mock_sentry_api):
    mock_instance = mock_sentry_api.return_value
    mock_instance.get_events.return_value = [
        {
            "eventID": "abc123",
            "dateCreated": "2023-01-01T00:00:00Z",
            "message": "Test event message",
            "location": "engine/agents/tests/test_sentry_tools.py",
            "culprit": "test_sentry_tools.py",
        }
    ]

    result = get_sentry_events("12345", "fake_api_key", "fake_org")
    assert "Found 1 events for issue ID" in result
    assert "Test event message" in result
    assert "engine/agents/tests/test_sentry_tools.py" in result
