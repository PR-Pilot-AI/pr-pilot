import logging
from datetime import datetime
import requests
from langchain.tools import Tool
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field

from engine.models.task_event import TaskEvent

logger = logging.getLogger(__name__)


class SentryAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://sentry.io/api/0"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def search_issues(self, query: str) -> dict:
        url = f"{self.base_url}/issues/?query={query}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_events(self, issue_id: str) -> dict:
        url = f"{self.base_url}/issues/{issue_id}/events/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


def search_sentry_issues(query: str, api_key: str) -> str:
    sentry = SentryAPI(api_key)
    try:
        issues = sentry.search_issues(query)
        TaskEvent.add(
            actor="assistant",
            action="search_sentry_issues",
            target=query,
            message=f"Searched for Sentry issues and found {len(issues)} matches for query '{query}'",
        )
        if issues:
            assembled_hits = "---\n"
            for issue in issues:
                assembled_hits += f"Title: {issue['title']}\n"
                assembled_hits += f"ID: {issue['id']}\n"
                assembled_hits += f"URL: {issue['permalink']}\n"
                assembled_hits += f"Status: {issue['status']}\n"
                assembled_hits += f"Count: {issue['count']}\n"
                assembled_hits += f"First Seen: {issue['firstSeen']}\n"
                assembled_hits += f"Last Seen: {issue['lastSeen']}\n"
                assembled_hits += "---\n"
            return f"Found {len(issues)} issues matching the query '{query}':\n\n{assembled_hits}"
        else:
            return f"No issues found matching the query '{query}'."
    except requests.RequestException as e:
        msg = f"Error searching Sentry issues: {str(e)}"
        logger.error(msg)
        return msg


def get_sentry_events(issue_id: str, api_key: str) -> str:
    sentry = SentryAPI(api_key)
    try:
        events = sentry.get_events(issue_id)
        TaskEvent.add(
            actor="assistant",
            action="get_sentry_events",
            target=issue_id,
            message=f"Retrieved {len(events)} events for issue ID '{issue_id}'",
        )
        if events:
            assembled_events = "---\n"
            for event in events:
                assembled_events += f"Event ID: {event['eventID']}\n"
                assembled_events += f"Timestamp: {event['dateCreated']}\n"
                assembled_events += f"Message: {event['message']}\n"
                assembled_events += "---\n"
            return f"Found {len(events)} events for issue ID '{issue_id}':\n\n{assembled_events}"
        else:
            return f"No events found for issue ID '{issue_id}'."
    except requests.RequestException as e:
        msg = f"Error retrieving events for issue ID '{issue_id}': {str(e)}"
        logger.error(msg)
        return msg


# Define a schema for the input parameters
class SearchSentryIssuesInput(BaseModel):
    query: str = Field(..., title="Query to search Sentry issues")


class GetSentryEventsInput(BaseModel):
    issue_id: str = Field(..., title="ID of the Sentry issue to get events for")


SEARCH_TOOL_DESCRIPTION = """
Search Sentry issues based on a query.
"""


GET_EVENTS_TOOL_DESCRIPTION = """
Get events for a specific Sentry issue ID.
"""


def list_sentry_tools(api_key: str) -> list:
    search_tool = Tool(
        name="search_sentry_issues",
        func=lambda query: search_sentry_issues(query, api_key),
        description=SEARCH_TOOL_DESCRIPTION,
    )

    get_events_tool = StructuredTool(
        name="get_sentry_events",
        func=lambda issue_id: get_sentry_events(issue_id, api_key),
        description=GET_EVENTS_TOOL_DESCRIPTION,
        args_schema=GetSentryEventsInput,
    )

    return [search_tool, get_events_tool]
