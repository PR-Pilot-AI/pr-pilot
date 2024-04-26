"""Global fixtures for pytest."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from engine.models.task import Task


@pytest.fixture(autouse=True)
def mock_chat_openai():
    with patch("langchain_openai.ChatOpenAI", new_callable=MagicMock) as mock:
        yield mock


@pytest.fixture
def task():
    task = Task.objects.create(
        issue_number=123,
        installation_id=123,
        comment_id=123,
        pilot_command="this is a test",
        github_user="test_user",
        github_project="test_project",
    )
    settings.TASK_ID = task.id
    return task
