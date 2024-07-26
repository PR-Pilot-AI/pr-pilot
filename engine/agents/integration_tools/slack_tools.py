import logging
import re
from datetime import datetime

from langchain.tools import Tool
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from engine.models.task_event import TaskEvent

logger = logging.getLogger(__name__)


def translate_markdown(markdown):
    """Translate Markdown into Slack-compatible format"""
    regex = r"\[([^\]]+)\]\(([^)]+)\)"
    return re.sub(regex, r"<\2|\1>", markdown).replace("**", "*")


def search_slack_messages(query: str, user_token: str) -> str:
    client = WebClient(token=user_token)
    try:
        response = client.search_messages(query=query)
        matches = response["messages"]["matches"]
        TaskEvent.add(
            actor="assistant",
            action="search_slack_messages",
            target=query,
            message=f"Found {len(matches)} Slack messages for query '{query}'",
        )
        if matches:
            assembled_hits = "---\n"
            for match in matches:
                unix_timestamp = match["ts"].split(".")[0]
                datetime_str = datetime.utcfromtimestamp(int(unix_timestamp)).strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )
                assembled_hits += f"Link: {match['permalink']}\n"
                assembled_hits += f"{datetime_str} @{match['username']} said:\n```\n{match['text']}\n```\n---\n"
            return f"Found {len(matches)} messages matching the query '{query}':\n\n{assembled_hits}"
        else:
            return f"No messages found matching the query '{query}'."
    except SlackApiError as e:
        msg = f"Error searching Slack messages: {e.response['error']}"
        logger.error(msg)
        return msg


def post_slack_message_to_channel(channel: str, message: str, bot_token: str) -> str:
    """Post a message to a Slack channel."""
    client = WebClient(token=bot_token)
    try:
        # Post the message
        channel = channel.lstrip("#")
        response = client.chat_postMessage(
            channel=channel, text=translate_markdown(message)
        )

        # Extract channel ID and timestamp
        channel_id = response["channel"]
        timestamp = response["ts"].replace(".", "")

        # Fetch the workspace domain
        team_info = client.team_info()
        workspace_domain = team_info["team"]["domain"]

        # Construct message URL
        message_url = (
            f"https://{workspace_domain}.slack.com/archives/{channel_id}/p{timestamp}"
        )

        TaskEvent.add(
            actor="assistant",
            action="post_slack_message",
            target=channel,
            message=f"Post [message]({message_url}) to channel #{channel}",
        )

        return f"Message posted to channel #{channel} successfully: {message_url}"
    except SlackApiError as e:
        msg = f"Error posting message to channel #{channel}: {e.response['error']}"
        logger.error(msg)
        return msg


# Define a schema for the input parameters
class PostSlackMessageInput(BaseModel):
    channel: str = Field(..., title="Slack channel to post the message to")
    message: str = Field(..., title="The message to post")


class DirectSlackMessageInput(BaseModel):
    user_email: str = Field(..., title="Email address of the Slack user")
    message: str = Field(..., title="The message to send to the user")


SEARCH_TOOL_DESCRIPTION = """
Search Slack messages based on a query.
Filters:
- in:channel (e.g. "in:#channel")
- from:user (e.g. "from:@username")
- during:day/month/year (e.g. "during:Yesterday", "during:Today", "during:June", "during:2021")
- before/after/on:date (e.g. "before:2021-06-01", "after:2021-06-01", "on:2021-06-01")
- has:reaction (e.g. "has::eyes:")

You can combine multiple filters, e.g. "in:#general in:#random from:@username during:Yesterday during:Today has::eyes:"
"""


def list_slack_tools(bot_token: str, user_token: str) -> list:
    search_tool = Tool(
        name="search_slack_workspace",
        func=lambda query: search_slack_messages(query, user_token),
        description=SEARCH_TOOL_DESCRIPTION,
    )

    post_tool = StructuredTool(
        name="post_slack_message",
        func=lambda channel, message: post_slack_message_to_channel(
            channel, message, bot_token
        ),
        description="Post a message to a Slack channel.",
        args_schema=PostSlackMessageInput,
    )

    return [search_tool, post_tool]
