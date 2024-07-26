import logging

import requests
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field

from engine.models.task_event import TaskEvent

logger = logging.getLogger(__name__)


class SentryAPI:
    def __init__(self, api_key: str, org: str):
        self.api_key = api_key
        self.org = org
        self.base_url = "https://sentry.io/api/0"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def search_issues(self, query: str, project: str) -> dict:
        url = f"{self.base_url}/projects/{self.org}/{project}/issues/"
        response = requests.get(url, headers=self.headers, params={"query": query})
        response.raise_for_status()
        return response.json()

    def get_events(self, issue_id: str, include_stacktrace: bool) -> dict:
        url = f"{self.base_url}/organizations/{self.org}/issues/{issue_id}/events/"
        response = requests.get(
            url, headers=self.headers, params={"full": include_stacktrace}
        )
        response.raise_for_status()
        return response.json()


def search_sentry_issues(query: str, api_key: str, org: str, project_slug: str) -> str:
    sentry = SentryAPI(api_key, org)
    try:
        issues = sentry.search_issues(query, project_slug)
        TaskEvent.add(
            actor="assistant",
            action="search_sentry_issues",
            target=query,
            message=f"Found {len(issues)} Sentry issues for query '{query}'",
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


def get_sentry_events(
    issue_id: str, include_stacktrace: bool, api_key: str, org: str
) -> str:
    sentry = SentryAPI(api_key, org)
    try:
        events = sentry.get_events(issue_id, include_stacktrace)
        TaskEvent.add(
            actor="assistant",
            action="get_sentry_events",
            target=issue_id,
            message=f"Load {len(events)} events for Sentry issue ID '{issue_id}'",
        )
        if events:
            assembled_events = "---\n"
            for event in events:
                assembled_events += f"Timestamp: {event['dateCreated']}\n"
                assembled_events += f"Message: {event['message']}\n"
                assembled_events += f"Location: {event['location']}\n"
                assembled_events += f"culprit: {event['culprit']}\n"
                for tag in [
                    "environment",
                    "github_project",
                    "github_user",
                    "server_name",
                ]:
                    if tag in event:
                        assembled_events += f"{tag.capitalize()}: {event[tag]}\n"
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
    project_slug: str = Field(..., title="Slug of the Sentry project to search")


class GetSentryEventsInput(BaseModel):
    issue_id: str = Field(..., title="ID of the Sentry issue to get events for")
    include_stacktrace: bool = Field(
        default=False, title="Include stacktrace in events"
    )


SEARCH_TOOL_DESCRIPTION = """
Search Sentry issues based on a query.
Notes on filters:
- `>/</=2023-01-01T00:00:00` for date filters
- `-24h`, `-1d`, etc for relative date filters
"""


GET_EVENTS_TOOL_DESCRIPTION = """
Get events for a specific Sentry issue ID.
"""


def list_sentry_tools(api_key: str, org: str) -> list:
    search_tool = StructuredTool(
        name="search_sentry_issues",
        func=lambda query, project_slug: search_sentry_issues(
            query, api_key, org, project_slug
        ),
        description=SEARCH_TOOL_DESCRIPTION,
        args_schema=SearchSentryIssuesInput,
    )

    get_events_tool = StructuredTool(
        name="get_sentry_events",
        func=lambda issue_id, include_stacktrace: get_sentry_events(
            issue_id, include_stacktrace, api_key, org
        ),
        description=GET_EVENTS_TOOL_DESCRIPTION,
        args_schema=GetSentryEventsInput,
    )

    return [search_tool, get_events_tool]
