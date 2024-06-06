"""Unit tests for the TaskEngine class."""

from unittest.mock import patch, MagicMock

import pytest

from engine.models.task import Task
from engine.models.task_bill import TaskBill
from engine.task_engine import TaskEngine


@pytest.fixture(autouse=True)
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
        mocked_pr = MagicMock(spec=["title", "html_url", "number"])
        mocked_pr.title = "Test PR"
        mocked_pr.html_url = "http://example.com/pr"
        mocked_pr.number = 69

        mock_from_github = MagicMock()
        mock_from_github.return_value.create_pull_request = MagicMock(
            return_value=mocked_pr
        )
        MockClass.from_github = mock_from_github
        MockClass.return_value = MagicMock(
            is_active_open_source_project=MagicMock(return_value=False),
        )
        yield MockClass


@pytest.fixture(autouse=True)
def mock_repo_class():
    with patch("engine.task_engine.Repo") as MockClass:
        MockClass.return_value = MagicMock(
            branches=[],
            active_branch=MagicMock(name="main"),
        )
        yield


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
    engine.finalize_working_branch = MagicMock(return_value=False)
    engine.setup_working_branch = MagicMock(return_value="test-branch")
    engine.clone_github_repo = MagicMock()
    engine.generate_task_title = MagicMock()
    return engine


@pytest.mark.django_db
def test_bill_creation_correctness(task, engine):
    engine.run()
    latest_bill = TaskBill.objects.filter(task=task).first()
    assert latest_bill is not None
    assert latest_bill.task == task


@pytest.mark.django_db
def test_task_status_set_correctly(task, engine):
    engine.run()
    task.refresh_from_db()
    assert task.status == "completed"
    assert task.pr_number is None
    assert task.branch == ""


@pytest.mark.django_db
def test_pr_number_set(task, engine):
    # Simulate local changes in the repository
    engine.finalize_working_branch.return_value = True
    engine.run()
    task.refresh_from_db()
    assert task.status == "completed"
    assert task.pr_number == 69
    assert task.branch == "test-branch"
