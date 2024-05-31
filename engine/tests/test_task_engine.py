"""Unit tests for the TaskEngine class."""

from unittest.mock import patch, MagicMock

import pytest

from engine.models.task import Task
from engine.models.task_bill import TaskBill
from engine.task_engine import TaskEngine


@pytest.fixture
def mock_generate_pr_info():
    with patch("engine.task_engine.generate_pr_info") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_create_pr_pilot_agent():
    with patch("engine.task_engine.create_pr_pilot_agent") as mock:
        mock.return_value = MagicMock(
            invoke=MagicMock(return_value={"output": "Test Output"})
        )
        yield


@pytest.fixture(autouse=True)
def mock_get_installation_access_token():
    with patch("engine.task_engine.get_installation_access_token"):
        yield lambda: "test_token"


@pytest.fixture(autouse=True)
def mock_generate_task_title():
    with patch("engine.task_engine.generate_task_title") as mock:
        mock.return_value = "Test Task"
        yield


@pytest.fixture
def mock_project_from_github():
    with patch("engine.project.Project.from_github") as mock:
        mock.return_value.create_pull_request.return_value = MagicMock(
            title="Test PR", html_url="http://example.com/pr"
        )
        yield mock


@pytest.fixture(autouse=True)
def mock_github_client(mock_get_installation_access_token):
    with patch("engine.task_engine.Github") as MockClass:
        MockClass.return_value = MagicMock(
            get_repo=lambda x: MagicMock(
                default_branch="main", full_name="test_user/test_project"
            ),
        )
        yield


@pytest.fixture(autouse=True)
def mock_project_class():
    with patch("engine.task_engine.Project") as MockClass:
        MockClass.return_value = MagicMock(
            is_active_open_source_project=MagicMock(return_value=False),
        )
        yield


@pytest.fixture(autouse=True)
def mock_repo_class():
    with patch("engine.task_engine.Repo") as MockClass:
        MockClass.return_value = MagicMock(
            branches=[],
            active_branch=MagicMock(name="main"),
        )
        yield


@pytest.fixture
def mock_task_project():
    with patch.object(TaskEngine, "project", create=True) as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_clone_github_repo():
    with patch.object(TaskEngine, "clone_github_repo", create=True) as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_create_response_comment():
    with patch.object(Task, "create_response_comment", create=True) as mock:
        mock.return_value = MagicMock(id=123)
        yield


@pytest.fixture
def engine(task):
    engine = TaskEngine(task)
    # Mock engine.generate_task_title
    engine.generate_task_title = MagicMock()
    return engine


@pytest.mark.django_db
def test_bill_creation_correctness(
    mock_generate_pr_info, mock_project_from_github, mock_task_project, task, engine
):
    engine.run()
    latest_bill = TaskBill.objects.filter(task=task).first()
    assert latest_bill is not None
    assert latest_bill.task == task


@pytest.mark.django_db
def test_task_status_set_correctly(
    mock_generate_pr_info, mock_project_from_github, mock_task_project, task, engine
):
    engine.run()
    task.refresh_from_db()
    assert task.status == "completed"
    # Additional assertions can be made for different scenarios, such as when an exception occurs
