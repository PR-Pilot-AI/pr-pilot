import pytest
from unittest.mock import patch
from slack_sdk.errors import SlackApiError
from engine.agents.integration_tools.slack_tools import (
    search_slack_messages,
    post_slack_message_to_channel,
    list_slack_tools,
)


@pytest.fixture
def mock_web_client():
    with patch("engine.agents.integration_tools.slack_tools.WebClient") as mock:
        yield mock


@pytest.fixture
def mock_task_event():
    with patch("engine.agents.integration_tools.slack_tools.TaskEvent") as mock:
        yield mock


def test_search_slack_messages_success(mock_web_client, mock_task_event):
    mock_client = mock_web_client.return_value
    mock_client.search_messages.return_value = {
        "messages": {
            "matches": [
                {
                    "ts": "1625097600.000200",
                    "permalink": "http://example.com/message1",
                    "username": "user1",
                    "text": "Test message 1",
                },
                {
                    "ts": "1625097601.000300",
                    "permalink": "http://example.com/message2",
                    "username": "user2",
                    "text": "Test message 2",
                },
            ]
        }
    }

    result = search_slack_messages("test query", "user_token")
    assert "Found 2 messages matching the query 'test query'" in result
    assert "http://example.com/message1" in result
    assert "http://example.com/message2" in result


def test_search_slack_messages_no_matches(mock_web_client, mock_task_event):
    mock_client = mock_web_client.return_value
    mock_client.search_messages.return_value = {"messages": {"matches": []}}

    result = search_slack_messages("test query", "user_token")
    assert result == "No messages found matching the query 'test query'."


def test_search_slack_messages_error(mock_web_client, mock_task_event):
    mock_client = mock_web_client.return_value
    mock_client.search_messages.side_effect = SlackApiError(
        response={"error": "invalid_auth"}, message="Error"
    )

    result = search_slack_messages("test query", "user_token")
    assert result == "Error searching Slack messages: invalid_auth"


def test_post_message_success(mock_web_client, mock_task_event):
    mock_client = mock_web_client.return_value
    mock_client.chat_postMessage.return_value = {
        "channel": "C1234567890",
        "ts": "1625097600.000200",
    }
    mock_client.team_info.return_value = {"team": {"domain": "example"}}

    result = post_slack_message_to_channel("test_channel", "Test message", "bot_token")
    assert "Message posted to channel #test_channel successfully" in result
    assert "https://example.slack.com/archives/C1234567890/p1625097600000200" in result


def test_post_message_error(mock_web_client, mock_task_event):
    mock_client = mock_web_client.return_value
    mock_client.chat_postMessage.side_effect = SlackApiError(
        response={"error": "channel_not_found"}, message="Error"
    )

    result = post_slack_message_to_channel("test_channel", "Test message", "bot_token")
    assert result == "Error posting message to channel #test_channel: channel_not_found"


def test_list_slack_tools():
    tools = list_slack_tools("bot_token", "user_token")
    assert len(tools) == 2
    assert tools[0].name == "search_slack_workspace"
    assert tools[1].name == "post_slack_message"
