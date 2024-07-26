import json
import logging

import requests
from langchain.agents import Tool
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Field

from engine.models.task_event import TaskEvent

LINEAR_API_URL = "https://api.linear.app/graphql"

logger = logging.getLogger(__name__)


def run_graphql_query(api_key: str, query: str):
    """Run a GraphQL query on the Linear API."""
    headers = {
        "Authorization": f"{api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(LINEAR_API_URL, json={"query": query}, headers=headers)
    return response.json()


def get_team_id_by_name(api_key, team_name):
    query = """
    query {
      teams {
        nodes {
          id
          name
        }
      }
    }
    """
    response = run_graphql_query(api_key, query)
    teams = response["data"]["teams"]["nodes"]
    for team in teams:
        if team["name"].lower() == team_name.lower():
            return team["id"]
    raise ValueError(f"No team found with the name '{team_name}'")


class LinearCreateIssueInput(BaseModel):
    title: str = Field(..., title="Title of the issue")
    description: str = Field(..., title="Description of the issue")
    team_name: str = Field(..., title="Name of the team to create the issue in")


def list_linear_tools(api_key: str):
    """Create all tools for PR Pilot to use with Linear API."""

    def linear_search_tool(query: str):

        TaskEvent.add(
            actor="assistant",
            action="search_linear_workspace",
            message=f"Search Linear with query: \n\n```\n{query}\n```",
        )
        response = run_graphql_query(api_key, query)
        if "errors" in response:
            message = (
                f"Error searching Linear workspace: {response['errors'][0]['message']}"
            )
            logger.error(message)
            logger.error(response)
            TaskEvent.add(
                actor="assistant",
                action="error",
                message=message,
            )
        return json.dumps(response, indent=2)

    def create_linear_issue_tool(title: str, description: str, team_name: str):

        team_id = get_team_id_by_name(api_key, team_name)
        query = f"""
        mutation IssueCreate {{
            issueCreate(
                input: {{
                    title: "{title}"
                    description: "{description}"
                    teamId: "{team_id}"
                }}
            ) {{
            success
                issue {{
                    id
                    title
                    url
                }}
            }}
        }}
        """
        response = run_graphql_query(api_key, query)
        if "errors" in response:
            message = f"Error creating Linear issue: {response['errors'][0]['message']}"
            issue_id = None
        else:
            issue = response["data"]["issueCreate"]["issue"]
            issue_link = issue["url"]
            issue_id = issue["id"]
            message = f"Create new Linear issue [{issue['title']}]({issue_link}) in team `{team_name}`"
        TaskEvent.add(
            actor="assistant",
            action="create_linear_issue",
            target=issue_id,
            message=message,
        )
        return message

    return [
        Tool(
            name="search_linear_workspace",
            func=linear_search_tool,
            description="Search the user's Linear workspace. Parameters: \n"
            "query (str): The GraphQL search query.",
        ),
        StructuredTool(
            name="create_linear_issue",
            func=create_linear_issue_tool,
            args_schema=LinearCreateIssueInput,
            description="Create a new issue in the user's Linear workspace.",
        ),
    ]
