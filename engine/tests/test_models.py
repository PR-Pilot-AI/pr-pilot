from unittest.mock import patch, MagicMock

import pytest

from engine.models.cost_item import CostItem
from engine.models.task import Task
from engine.task_scheduler import SchedulerError


@pytest.fixture(autouse=True)
def mock_get_installation_access_token():
    with patch("engine.models.task.get_installation_access_token"):
        yield lambda: "test_token"


@pytest.fixture(autouse=True)
def mock_github_client(mock_get_installation_access_token):
    with patch("engine.models.task.Github") as MockClass:
        MockClass.return_value = MagicMock(
            get_repo=MagicMock(
                return_value=MagicMock(
                    default_branch="main", full_name="test_user/test_project"
                )
            ),
        )
        yield


@pytest.mark.django_db
def test_credits():
    cost_item = CostItem(
        title="Test Item",
        model_name="TestModel",
        prompt_token_count=100,
        completion_token_count=200,
        requests=1,
        total_cost_usd=10.0,
    )
    cost_item.save()

    # Assuming CREDIT_MULTIPLIER is set to 2 for this test
    expected_credits = 10.0 * 2 * 100
    assert (
        cost_item.credits == expected_credits
    ), "The credits calculation did not match the expected value."


@pytest.mark.django_db
def test_task_only_schedules_if_user_can_write(task):
    task.github.get_repo.return_value.get_collaborator_permission.return_value = "write"
    task.schedule()
    task.refresh_from_db()
    assert task.status == "scheduled"

    task.github.get_repo.return_value.get_collaborator_permission.return_value = "read"
    with pytest.raises(SchedulerError):
        task.schedule()


@pytest.mark.django_db
def test_task_would_reach_rate_limit(task):
    task.github_project = "test_user/test_project"
    task.save()

    # Create 8 tasks in the last 10 minutes
    for i in range(18):
        Task.objects.create(
            github_project="test_user/test_project",
            status="scheduled",
            installation_id=123,
            github_user="test_user",
            title="Test Task",
            user_request="Test Request",
        )

    assert (
        not task.would_reach_rate_limit()
    ), "The task should not reach the rate limit with 9 tasks in the last 10 minutes."

    # Create another task
    Task.objects.create(
        github_project="test_user/test_project",
        status="scheduled",
        installation_id=123,
        github_user="test_user",
        title="Test Task",
        user_request="Test Request",
    )

    assert task.would_reach_rate_limit(), "The task should reach the rate limit"
