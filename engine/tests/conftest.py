"""Global fixtures for pytest."""

import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_chat_openai():
    with patch('engine.langchain_openai.ChatOpenAI', new_callable=MagicMock) as mock:
        yield mock
