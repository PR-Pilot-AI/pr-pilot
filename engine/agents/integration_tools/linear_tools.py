import requests

from langchain.agents import Tool

from engine.models.task_event import TaskEvent

LINEAR_API_URL = "https://api.linear.app/graphql"


def list_linear_tools(api_key: str):
    """Create all tools for PR Pilot to use with Linear API."""

    def linear_search_tool(query: str):
        headers = {
            "Authorization": f"{api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(LINEAR_API_URL, json={"query": query}, headers=headers)
        TaskEvent.add(
            actor="assistant",
            action="search_linear_workspace",
            target=query,
            message=f"Performed a Linear search with query '{query}'",
        )
        return response.json()

    return [
        Tool(
            name="search_linear_workspace",
            func=linear_search_tool,
            description="Search the user's Linear workspace. Parameters: \n"
            "query (str): The GraphQL search query.",
        )
    ]
