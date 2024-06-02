import base64
import os
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
    api_key, key = UserAPIKey.objects.create_key(
        name="for-testing", username="testuser"
    )
    return key


@pytest.fixture
def github_project():
    return "test/hello-world"


@pytest.fixture()
def mock_get_installation_access_token():
    with patch("engine.models.task.get_installation_access_token"):
        yield lambda: "test_token"


@pytest.fixture(autouse=True)
def mock_github_client(github_project, mock_get_installation_access_token):
    with patch("engine.models.task.Github") as MockClass:
        MockClass.return_value = MagicMock(
            get_repo=lambda x: MagicMock(
                default_branch="main",
                full_name=github_project,
                get_collaborator_permission=lambda x: "write",
            ),
        )
        yield


@pytest.fixture
def github_repo(github_project):
    account = GitHubAccount.objects.create(
        account_id=1,
        login="test",
        avatar_url="http://example.com/avatar",
        html_url="http://example.com",
    )
    installation = GitHubAppInstallation.objects.create(
        installation_id=123,
        app_id=1,
        target_id=1,
        target_type="Organization",
        account=account,
    )
    return GithubRepository.objects.create(
        id=1, full_name=github_project, name="hello-world", installation=installation
    )


@pytest.mark.django_db
def test_create_task_via_api(api_key, github_repo):
    response = client.post(
        "/api/tasks/",
        {
            "prompt": "Hello, World!",
            "github_repo": github_repo.full_name,
        },
        headers={"X-Api-Key": api_key},
        format="json",
    )
    assert response.status_code == 201
    task = Task.objects.first()
    assert task is not None
    assert task.user_request == "Hello, World!"
    assert task.status == "scheduled"
    assert task.github_user == "testuser"
    assert task.github_project == github_repo.full_name
    assert task.installation_id == github_repo.installation.installation_id
    assert not task.issue_number
    assert not task.pr_number
    assert (
        client.get(
            f"/api/tasks/{str(task.id)}/", headers={"X-Api-Key": api_key}
        ).status_code
        == 200
    )


@pytest.mark.django_db
@patch("api.views.get_installation_access_token", return_value="test_token")
@patch("api.views.Github")
def test_create_task_via_api_with_pr_number(
    mock_github, mock_get_token, api_key, github_repo
):
    # Setting up the nested mock structure
    mock_repo = MagicMock(default_branch="main", full_name="test/hello-world")
    mock_pull = MagicMock(
        head=MagicMock(ref="feature-branch"), base=MagicMock(ref="main")
    )
    mock_repo.get_pull.return_value = mock_pull
    mock_github.return_value.get_repo.return_value = mock_repo

    # Make the POST request
    response = client.post(
        "/api/tasks/",
        {
            "prompt": "Hello, World!",
            "github_repo": github_repo.full_name,
            "pr_number": 123,
        },
        headers={"X-Api-Key": api_key},
        format="json",
    )

    assert response.status_code == 201
    task = Task.objects.first()
    assert task.pr_number == 123
    assert task.github_project == github_repo.full_name
    assert task.head == "feature-branch"
    assert task.base == "main"
    assert task.gpt_model == "gpt-4-turbo"


@pytest.mark.django_db
def test_create_task_via_api__repo_not_found(api_key):
    response = client.post(
        "/api/tasks/",
        {
            "prompt": "Hello, World!",
            "github_repo": "test/hello-world",
        },
        headers={"X-Api-Key": api_key},
        format="json",
    )
    assert response.status_code == 404
    assert not Task.objects.exists()


@pytest.mark.django_db
def test_image_upload(api_key, github_repo):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(this_dir, "fixtures/screenshot.png"), "rb") as image:
        base_64_image = base64.b64encode(image.read()).decode()
        response = client.post(
            "/api/tasks/",
            {
                "prompt": "Hello, World!",
                "github_repo": github_repo.full_name,
                "image": base_64_image,
            },
            headers={"X-Api-Key": api_key},
            format="json",
        )
        assert response.status_code == 201
        task = Task.objects.first()
        assert task.image is not None
        assert base_64_image == base64.b64encode(task.image).decode()
