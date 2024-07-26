from unittest.mock import patch

import pytest

from engine.agents.integration_tools.linear_tools import (
    run_graphql_query,
    get_team_id_by_name,
    list_linear_tools,
    LINEAR_API_URL,
)


@pytest.fixture(autouse=True)
def mock_task_event():
    with patch("engine.agents.integration_tools.linear_tools.TaskEvent") as mock:
        yield mock


@pytest.fixture
def api_key():
    return "test_api_key"


@pytest.fixture
def team_name():
    return "Test Team"


@pytest.fixture
def graphql_response():
    return {
        "data": {
            "teams": {
                "nodes": [
                    {"id": "team1", "name": "Test Team"},
                    {"id": "team2", "name": "Another Team"},
                ]
            }
        }
    }


def test_run_graphql_query(api_key):
    query = "{ teams { nodes { id name } } }"
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"data": "test_data"}
        response = run_graphql_query(api_key, query)
        mock_post.assert_called_once_with(
            LINEAR_API_URL,
            json={"query": query},
            headers={
                "Authorization": f"{api_key}",
                "Content-Type": "application/json",
            },
        )
        assert response == {"data": "test_data"}


def test_get_team_id_by_name(api_key, team_name, graphql_response):
    with patch(
        "engine.agents.integration_tools.linear_tools.run_graphql_query"
    ) as mock_run_query:
        mock_run_query.return_value = graphql_response
        team_id = get_team_id_by_name(api_key, team_name)
        assert team_id == "team1"


def test_get_team_id_by_name_not_found(api_key):
    with patch(
        "engine.agents.integration_tools.linear_tools.run_graphql_query"
    ) as mock_run_query:
        mock_run_query.return_value = {"data": {"teams": {"nodes": []}}}
        with pytest.raises(
            ValueError, match="No team found with the name 'Nonexistent Team'"
        ):
            get_team_id_by_name(api_key, "Nonexistent Team")


def test_list_linear_tools(api_key):
    tools = list_linear_tools(api_key)
    assert len(tools) == 2
    assert tools[0].name == "search_linear_workspace"
    assert tools[1].name == "create_linear_issue"


def test_linear_search_tool(api_key):
    tools = list_linear_tools(api_key)
    search_tool = tools[0]
    query = "{ issues { nodes { id title } } }"
    with patch(
        "engine.agents.integration_tools.linear_tools.run_graphql_query"
    ) as mock_run_query:
        mock_run_query.return_value = {"data": "search_results"}
        result = search_tool.func(query)
        assert result == '{\n  "data": "search_results"\n}'


def test_create_linear_issue_tool(api_key, team_name, graphql_response):
    tools = list_linear_tools(api_key)
    create_tool = tools[1]
    title = "Test Issue"
    description = "This is a test issue."
    with patch(
        "engine.agents.integration_tools.linear_tools.run_graphql_query"
    ) as mock_run_query:
        mock_run_query.side_effect = [
            graphql_response,  # Response for get_team_id_by_name
            {
                "data": {
                    "issueCreate": {
                        "issue": {
                            "id": "issue1",
                            "title": title,
                            "url": "http://linear.app/issue1",
                        }
                    }
                }
            },  # Response for create issue
        ]
        result_message = create_tool.func(
            title=title, description=description, team_name=team_name
        )
        assert (
            result_message
            == f"Create new Linear issue [{title}](http://linear.app/issue1) in team `{team_name}`"
        )


def test_create_linear_issue_tool_error(api_key, team_name, graphql_response):
    tools = list_linear_tools(api_key)
    create_tool = tools[1]
    title = "Test Issue"
    description = "This is a test issue."
    with patch(
        "engine.agents.integration_tools.linear_tools.run_graphql_query"
    ) as mock_run_query:
        mock_run_query.side_effect = [
            graphql_response,  # Response for get_team_id_by_name
            {
                "errors": [{"message": "Error creating issue"}]
            },  # Response for create issue
        ]
        result_message = create_tool.func(
            title=title, description=description, team_name=team_name
        )
        assert result_message == "Error creating Linear issue: Error creating issue"
