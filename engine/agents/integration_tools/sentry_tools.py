import logging
from datetime import datetime

from langchain.tools import Tool
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
import requests

from engine.models.task_event import TaskEvent

logger = logging.getLogger(__name__)


class SentryEventInput(BaseModel):
    project_id: str = Field(..., title="Sentry project ID")
    event_id: str = Field(..., title="Sentry event ID")


class SentryIssueInput(BaseModel):
    project_id: str = Field(..., title="Sentry project ID")
    issue_id: str = Field(..., title="Sentry issue ID")


def fetch_sentry_event(project_id: str, event_id: str, api_key: str) -> str:
    url = f"https://sentry.io/api/0/projects/{project_id}/events/{event_id}/"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        event = response.json()
        TaskEvent.add(
            actor="assistant",
            action="fetch_sentry_event",
            target=event_id,
            message=f"Fetched Sentry event {event_id} from project {project_id}",
        )
        return event
    else:
        msg = f"Error fetching Sentry event: {response.status_code} - {response.text}"
        logger.error(msg)
        return msg


def fetch_sentry_issue(project_id: str, issue_id: str, api_key: str) -> str:
    url = f"https://sentry.io/api/0/projects/{project_id}/issues/{issue_id}/"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        issue = response.json()
        TaskEvent.add(
            actor="assistant",
            action="fetch_sentry_issue",
            target=issue_id,
            message=f"Fetched Sentry issue {issue_id} from project {project_id}",
        )
        return issue
    else:
        msg = f"Error fetching Sentry issue: {response.status_code} - {response.text}"
        logger.error(msg)
        return msg


FETCH_EVENT_DESCRIPTION = """
Fetch a specific event from a Sentry project using the event ID.
"""


FETCH_ISSUE_DESCRIPTION = """
Fetch a specific issue from a Sentry project using the issue ID.
"""


def list_sentry_tools(api_key: str) -> list:
    fetch_event_tool = StructuredTool(
        name="fetch_sentry_event",
        func=lambda project_id, event_id: fetch_sentry_event(project_id, event_id, api_key),
        description=FETCH_EVENT_DESCRIPTION,
        args_schema=SentryEventInput,
    )

    fetch_issue_tool = StructuredTool(
        name="fetch_sentry_issue",
        func=lambda project_id, issue_id: fetch_sentry_issue(project_id, issue_id, api_key),
        description=FETCH_ISSUE_DESCRIPTION,
        args_schema=SentryIssueInput,
    )

    return [fetch_event_tool, fetch_issue_tool]
