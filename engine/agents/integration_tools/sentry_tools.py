import logging
from datetime import datetime
from typing import List

from langchain.tools import Tool
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
import requests

from engine.models.task_event import TaskEvent

logger = logging.getLogger(__name__)


class SentryEvent(BaseModel):
    id: str
    title: str
    culprit: str
    dateCreated: datetime
    permalink: str


class SentryIssue(BaseModel):
    id: str
    title: str
    culprit: str
    firstSeen: datetime
    lastSeen: datetime
    permalink: str


class FetchSentryEventsInput(BaseModel):
    project_id: str = Field(..., title="Sentry project ID")
    limit: int = Field(10, title="Number of events to fetch")


class FetchSentryIssuesInput(BaseModel):
    project_id: str = Field(..., title="Sentry project ID")
    limit: int = Field(10, title="Number of issues to fetch")


def fetch_sentry_events(api_key: str, project_id: str, limit: int = 10) -> List[SentryEvent]:
    url = f"https://sentry.io/api/0/projects/{project_id}/events/"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"limit": limit}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    events = response.json()
    TaskEvent.add(
        actor="assistant",
        action="fetch_sentry_events",
        target=project_id,
        message=f"Fetched {len(events)} events for project {project_id}",
    )
    return [SentryEvent(**event) for event in events]


def fetch_sentry_issues(api_key: str, project_id: str, limit: int = 10) -> List[SentryIssue]:
    url = f"https://sentry.io/api/0/projects/{project_id}/issues/"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"limit": limit}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    issues = response.json()
    TaskEvent.add(
        actor="assistant",
        action="fetch_sentry_issues",
        target=project_id,
        message=f"Fetched {len(issues)} issues for project {project_id}",
    )
    return [SentryIssue(**issue) for issue in issues]


FETCH_EVENTS_TOOL_DESCRIPTION = """
Fetch recent events from a Sentry project.

Provide the Sentry project ID and the number of events to fetch.
"""


FETCH_ISSUES_TOOL_DESCRIPTION = """
Fetch recent issues from a Sentry project.

Provide the Sentry project ID and the number of issues to fetch.
"""


def list_sentry_tools(api_key: str) -> list:
    fetch_events_tool = StructuredTool(
        name="fetch_sentry_events",
        func=lambda project_id, limit: fetch_sentry_events(api_key, project_id, limit),
        description=FETCH_EVENTS_TOOL_DESCRIPTION,
        args_schema=FetchSentryEventsInput,
    )

    fetch_issues_tool = StructuredTool(
        name="fetch_sentry_issues",
        func=lambda project_id, limit: fetch_sentry_issues(api_key, project_id, limit),
        description=FETCH_ISSUES_TOOL_DESCRIPTION,
        args_schema=FetchSentryIssuesInput,
    )

    return [fetch_events_tool, fetch_issues_tool]
