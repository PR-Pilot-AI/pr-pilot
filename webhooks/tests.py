from unittest.mock import patch
import pytest
from webhooks.handlers.util import install_repository
from webhooks.models import GitHubAppInstallation, GithubRepository, GitHubAccount
from api.models import UserAPIKey

@pytest.mark.django_db
@patch('webhooks.handlers.util.Github')
def test_install_repository_truncates_api_key_name(mock_github):
    # Setup mock GitHub account and installation
    account = GitHubAccount.objects.create(
        account_id=12345,
        login='testuser',
        avatar_url='http://example.com/avatar',
        html_url='http://example.com'
    )
    installation = GitHubAppInstallation.objects.create(
        installation_id=123,
        app_id=1,
        target_id=account.account_id,
        target_type='User',
        account=account
    )
    repo_data = {
        'full_name': 'a' * 60,  # Simulate a long repository name
        'name': 'test-repo'
    }
    # Mock the GitHub interaction
    mock_github.return_value.get_repo.return_value = MagicMock()

    # Call the function under test
    install_repository(installation, repo_data, 'testuser')

    # Verify the API key name was truncated
    api_key = UserAPIKey.objects.last()
    assert len(api_key.name) <= 49, "API key name should be truncated to 49 characters"
