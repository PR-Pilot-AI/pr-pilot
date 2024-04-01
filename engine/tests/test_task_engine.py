"""Unit tests for the TaskEngine class."""

import pytest
from unittest.mock import patch, MagicMock

from engine.task_engine import TaskEngine
from engine.models import Task
from engine.project import Project


@pytest.fixture
def mock_generate_pr_info():
    with patch('engine.task_engine.generate_pr_info') as mock:
        yield mock


@pytest.fixture
def mock_project_from_github():
    with patch('engine.project.Project.from_github') as mock:
        mock.return_value.create_pull_request.return_value = MagicMock(title="Test PR", html_url="http://example.com/pr")
        yield mock


@pytest.fixture
def mock_task_project():
    with patch.object(TaskEngine, 'project', create=True) as mock:
        yield mock


@pytest.mark.django_db
def test_bill_creation_correctness(mock_generate_pr_info, mock_project_from_github, mock_task_project):
    task = Task.objects.create(github_user="test_user", github_project="test_project")
    task_engine = TaskEngine(task)
    task_engine.run()
    # Assuming TaskBill model has a method `get_latest_bill_for_task` to fetch the latest bill for a task
    latest_bill = TaskBill.get_latest_bill_for_task(task.id)
    assert latest_bill is not None
    assert latest_bill.task == task
    # Further assertions can be made based on the expected bill properties


@pytest.mark.django_db
def test_project_from_github_called_correctly(mock_generate_pr_info, mock_project_from_github, mock_task_project):
    task = Task.objects.create(github_user="test_user", github_project="test_project")
    task_engine = TaskEngine(task)
    task_engine.run()
    mock_project_from_github.assert_called_once()
    mock_project_from_github.return_value.create_pull_request.assert_called_with(
        title=mock.ANY, body=mock.ANY, head=mock.ANY, labels=mock.ANY
    )


@pytest.mark.django_db
def test_task_status_set_correctly(mock_generate_pr_info, mock_project_from_github, mock_task_project):
    task = Task.objects.create(github_user="test_user", github_project="test_project")
    task_engine = TaskEngine(task)
    task_engine.run()
    task.refresh_from_db()
    assert task.status == "completed"
    # Additional assertions can be made for different scenarios, such as when an exception occurs
