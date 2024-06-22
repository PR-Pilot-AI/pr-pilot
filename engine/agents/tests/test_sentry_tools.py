import pytest
from unittest.mock import patch, MagicMock
from engine.agents.integration_tools.sentry_tools import fetch_sentry_events, fetch_sentry_issues, list_sentry_tools


@pytest.fixture

def mock_sentry_response():
    with patch('requests.get') as mock_get:
        yield mock_get


def test_fetch_sentry_events(mock_sentry_response):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "1",
            "title": "Error 1",
            "culprit": "function_1",
            "dateCreated": "2023-01-01T00:00:00Z",
            "permalink": "http://example.com/event/1"
        }
    ]
    mock_response.status_code = 200
    mock_sentry_response.return_value = mock_response

    events = fetch_sentry_events(api_key="fake_api_key", project_id="fake_project_id", limit=1)
    assert len(events) == 1
    assert events[0].id == "1"
    assert events[0].title == "Error 1"


def test_fetch_sentry_issues(mock_sentry_response):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "1",
            "title": "Issue 1",
            "culprit": "function_1",
            "firstSeen": "2023-01-01T00:00:00Z",
            "lastSeen": "2023-01-02T00:00:00Z",
            "permalink": "http://example.com/issue/1"
        }
    ]
    mock_response.status_code = 200
    mock_sentry_response.return_value = mock_response

    issues = fetch_sentry_issues(api_key="fake_api_key", project_id="fake_project_id", limit=1)
    assert len(issues) == 1
    assert issues[0].id == "1"
    assert issues[0].title == "Issue 1"


def test_list_sentry_tools():
    tools = list_sentry_tools(api_key="fake_api_key")
    assert len(tools) == 2
    assert tools[0].name == "fetch_sentry_events"
    assert tools[1].name == "fetch_sentry_issues"
