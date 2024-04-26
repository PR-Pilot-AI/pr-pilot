from unittest.mock import patch, MagicMock

import pytest

from engine.task_scheduler import TaskScheduler


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
@pytest.mark.parametrize(
    "permission,can_write",
    [
        ("write", True),
        ("read", False),
        ("admin", True),
        ("none", False),
        ("", False),
    ],
)
def test_user_can_write(task, permission, can_write):
    scheduler = TaskScheduler(task)
    task.github.get_repo.return_value.get_collaborator_permission.return_value = (
        permission
    )
    assert scheduler.user_can_write() == can_write
