import logging

from langchain.tools import Tool
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from engine.models.task_event import TaskEvent

logger = logging.getLogger(__name__)


def search_slack_messages(query: str, bot_token: str) -> str:
    client = WebClient(token=bot_token)
    try:
        response = client.search_messages(query=query)
        matches = response["messages"]["matches"]
        TaskEvent.add(
            actor="assistant",
            action="search_slack_messages",
            target=query,
            message=f"Searched for Slack messages and found {len(matches)} matches for query '{query}'",
        )
        if matches:
            assembled_hits = "---\n"
            for match in matches:
                assembled_hits += f"{match['user']} said: {match['text']}\n---\n"
            return f"Found {len(matches)} messages matching the query '{query}':\n\n{assembled_hits}"
        else:
            return f"No messages found matching the query '{query}'."
    except SlackApiError as e:
        msg = f"Error searching Slack messages: {e.response['error']}"
        logger.error(msg)
        return msg


def post_message(channel: str, message: str, bot_token: str) -> str:
    client = WebClient(token=bot_token)
    try:
        client.chat_postMessage(channel=channel, text=message)
        TaskEvent.add(
            actor="assistant",
            action="post_slack_message",
            target=channel,
            message=f"Posted message to channel #{channel}: {message}",
        )
        return f"Message successfully posted message to channel #{channel}"
    except SlackApiError as e:
        msg = f"Error posting message to channel #{channel}: {e.response['error']}"
        logger.error(msg)
        return msg


def list_slack_tools(bot_token: str) -> list:
    search_tool = Tool(
        name="search_slack_workspace",
        func=lambda query: search_slack_messages(query, bot_token),
        description="Search Slack messages based on a query. Parameters: \n"
        "query (str): The search query.",
    )

    post_tool = Tool(
        name="post_slack_message",
        func=lambda channel, message: post_message(channel, message, bot_token),
        description="Post a message to a Slack channel. Parameters: \n"
        "channel (str): The Slack channel to post the message to. \n"
        "message (str): The message to post.",
    )

    return [search_tool, post_tool]
