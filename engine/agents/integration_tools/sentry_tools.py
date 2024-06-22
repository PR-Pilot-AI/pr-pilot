import logging
import requests
from langchain.tools import Tool
from pydantic.v1 import BaseModel, Field

logger = logging.getLogger(__name__)


class SentryEventInput(BaseModel):
    event_id: str = Field(..., title="Sentry Event ID")


class SentryIssueInput(BaseModel):
    issue_id: str = Field(..., title="Sentry Issue ID")


def fetch_sentry_event(event_id: str, api_key: str) -> str:
    url = f"https://sentry.io/api/0/issues/{event_id}/events/"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error fetching Sentry event: {response.status_code} {response.text}")
        return f"Error fetching Sentry event: {response.status_code}"


def fetch_sentry_issue(issue_id: str, api_key: str) -> str:
    url = f"https://sentry.io/api/0/issues/{issue_id}/"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error fetching Sentry issue: {response.status_code} {response.text}")
        return f"Error fetching Sentry issue: {response.status_code}"


def list_sentry_tools(api_key: str) -> list:
    fetch_event_tool = Tool(
        name="fetch_sentry_event",
        func=lambda event_id: fetch_sentry_event(event_id, api_key),
        description="Fetch details of a Sentry event by its ID.",
        args_schema=SentryEventInput,
    )

    fetch_issue_tool = Tool(
        name="fetch_sentry_issue",
        func=lambda issue_id: fetch_sentry_issue(issue_id, api_key),
        description="Fetch details of a Sentry issue by its ID.",
        args_schema=SentryIssueInput,
    )

    return [fetch_event_tool, fetch_issue_tool]
