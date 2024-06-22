import logging
from datetime import datetime

from langchain.tools import Tool
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
import requests

from engine.models.task_event import TaskEvent

logger = logging.getLogger(__name__)


class SentryAPIKeyInput(BaseModel):
    api_key: str = Field(..., title="Sentry API Key")


def search_sentry_issues(api_key: str, query: str) -> str:
    url = "https://sentry.io/api/0/issues/"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"query": query}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        issues = response.json()
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
                assembled_hits += f"Link: {issue['permalink']}\n"
                assembled_hits += f"Status: {issue['status']}\n"
                assembled_hits += f"First seen: {issue['firstSeen']}\n"
                assembled_hits += f"Last seen: {issue['lastSeen']}\n"
                assembled_hits += f"Count: {issue['count']}\n"
                assembled_hits += f"User count: {issue['userCount']}\n"
                assembled_hits += "---\n"
            return f"Found {len(issues)} issues matching the query '{query}':\n\n{assembled_hits}"
        else:
            return f"No issues found matching the query '{query}'."
    except requests.RequestException as e:
        msg = f"Error searching Sentry issues: {str(e)}"
        logger.error(msg)
        return msg


def list_sentry_tools(api_key: str) -> list:
    search_tool = Tool(
        name="search_sentry_issues",
        func=lambda query: search_sentry_issues(api_key, query),
        description="Search Sentry issues based on a query.",
    )

    return [search_tool]
