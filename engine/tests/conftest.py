"""Global fixtures for pytest."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_chat_openai():
    with patch('langchain_openai.ChatOpenAI', new_callable=MagicMock) as mock:
        yield mock
