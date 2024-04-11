from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from engine.models import CostItem


@pytest.fixture(autouse=True)
def mock_get_installation_access_token():
    with patch('engine.models.get_installation_access_token'):
        yield lambda: "test_token"


@pytest.fixture(autouse=True)
def mock_github_client(mock_get_installation_access_token):
    with patch('engine.models.Github') as MockClass:
        MockClass.return_value = MagicMock(
            get_repo=MagicMock(return_value=MagicMock(default_branch="main", full_name="test_user/test_project")),
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
    assert cost_item.credits == expected_credits, "The credits calculation did not match the expected value."


@pytest.mark.django_db
@pytest.mark.parametrize("permission,can_write", [("write", True), ("read", False), ("admin", True), ("none", False), ("", False),])
def test_task_user_can_write(task, permission, can_write):
    task.github.get_repo.return_value.get_collaborator_permission.return_value = permission
    assert task.user_can_write() == can_write


@pytest.mark.django_db
def test_task_only_schedules_if_user_can_write(task):
    task.github.get_repo.return_value.get_collaborator_permission.return_value = "write"
    task.schedule()
    task.refresh_from_db()
    assert task.status == "scheduled"

    task.github.get_repo.return_value.get_collaborator_permission.return_value = "read"
    task.schedule()
    task.refresh_from_db()
    assert task.status == "failed"