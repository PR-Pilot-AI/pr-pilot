"""Global fixtures for pytest."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from accounts.models import PilotUser
from engine.models.task import Task


@pytest.fixture(autouse=True)
def mock_chat_openai():
    with patch("langchain_openai.ChatOpenAI", new_callable=MagicMock) as mock:
        yield mock


@pytest.fixture
def task(user):
    task = Task.objects.create(
        issue_number=123,
        installation_id=123,
        comment_id=123,
        pilot_command="this is a test",
        github_user=user.username,
        github_project="test_project",
    )
    settings.TASK_ID = task.id
    return task


@pytest.fixture
def user():
    return PilotUser.objects.create(
        username="test_user",
        email="test_user@pr-pilot.ai",
    )


@pytest.fixture(autouse=True)
def mock_get_channel_layer():
    with patch("engine.channels.async_to_sync"):
        with patch("engine.channels.get_channel_layer") as mock:
            yield mock
