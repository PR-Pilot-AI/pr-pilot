from unittest.mock import patch, MagicMock

import pytest
from rest_framework.test import APIClient

from api.models import UserAPIKey
from engine.models.task import Task
from webhooks.models import GithubRepository, GitHubAppInstallation, GitHubAccount

# Create your tests here.
client = APIClient()


@pytest.fixture
def api_key():
    api_key, key = UserAPIKey.objects.create_key(name="for-testing", username="testuser")
    return key


@pytest.fixture
def github_project():
    return "test/hello-world"


@pytest.fixture()
def mock_get_installation_access_token():
    with patch('engine.models.task.get_installation_access_token'):
        yield lambda: "test_token"


@pytest.fixture(autouse=True)
def mock_github_client(github_project, mock_get_installation_access_token):
    with patch('engine.models.task.Github') as MockClass:
        MockClass.return_value = MagicMock(
            get_repo=lambda x: MagicMock(default_branch="main", full_name=github_project,
                                         get_collaborator_permission=lambda x: "write"),
        )
        yield


@pytest.mark.django_db
def test_create_task_via_api(api_key, github_project):
    account = GitHubAccount.objects.create(account_id=1, login='test', avatar_url='http://example.com/avatar', html_url='http://example.com')
    installation = GitHubAppInstallation.objects.create(installation_id=123, app_id=1, target_id=1, target_type='Organization', account=account)
    repo = GithubRepository.objects.create(id=1, full_name=github_project, name='hello-world', installation=installation)
    response = client.post('/api/tasks/', headers={'X-Api-Key': api_key}, data={
        'prompt': 'Hello, World!',
        'github_repo': github_project,
    })
    assert response.status_code == 201
    task = Task.objects.first()
    assert task is not None
    assert task.user_request == 'Hello, World!'
    assert task.status == 'scheduled'
    assert task.github_user == 'testuser'
    assert task.github_project == github_project
    assert task.installation_id == installation.installation_id


@pytest.mark.django_db
def test_create_task_via_api__repo_not_found(api_key):
    response = client.post('/api/tasks/', headers={'X-Api-Key': api_key}, data={
        'prompt': 'Hello, World!',
        'github_repo': 'test/hello-world',
    })
    assert response.status_code == 404
    assert not Task.objects.exists()