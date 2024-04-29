import logging

from github import Github

from api.models import UserAPIKey
from webhooks.jwt_tools import get_installation_access_token
from webhooks.models import GithubRepository

GITHUB_SECRET_NAME = "PR_PILOT_API_KEY"


logger = logging.getLogger(__name__)


def install_repository(installation, repo_data, github_user):
    GithubRepository.objects.update_or_create(
        id=repo_data["id"],
        defaults={
            "full_name": repo_data["full_name"],
            "name": repo_data["name"],
            "installation": installation,
        },
    )
    g = Github(get_installation_access_token(installation.installation_id))
    repo = g.get_repo(repo_data["full_name"])
    api_key_exists = UserAPIKey.objects.filter(
        username=github_user, github_project=repo_data["full_name"]
    ).exists()
    if api_key_exists:
        logger.info(
            f"API key already exists for user @{github_user} on repository {repo_data['full_name']}"
        )
        if repo.get_secret(GITHUB_SECRET_NAME):
            logger.info(
                f"Secret {GITHUB_SECRET_NAME} already exists for "
                f"repository {repo_data['full_name']}"
            )
            return
        # Delete existing API key
        logger.info(
            f"Repository doesn't have secret. Re-creating API key for "
            f"user @{github_user} on repository {repo_data['full_name']}"
        )
        UserAPIKey.objects.filter(
            username=github_user, github_project=repo_data["full_name"]
        ).delete()
    logger.info(
        f"Creating API key for user @{github_user} on repository {repo_data['full_name']}"
    )
    key_name = repo_data["full_name"][:49]
    api_key, key = UserAPIKey.objects.create_key(
        name=key_name,
        github_project=repo_data["full_name"],
        username=github_user,
    )

    logger.info(
        f"Creating secret {GITHUB_SECRET_NAME} for repository {repo_data['full_name']}"
    )
    repo.create_secret(GITHUB_SECRET_NAME, key)


def uninstall_repository(repo_data, github_user):
    try:
        repo = GithubRepository.objects.get(id=repo_data["id"])
        repo.delete()
        UserAPIKey.objects.filter(
            username=github_user, github_project=repo_data["full_name"]
        ).delete()
        logger.info(f"Repository {repo.full_name} uninstalled")
    except GithubRepository.DoesNotExist:
        logger.error(
            f'Tried to uninstall repository {repo_data["full_name"]}, but not found'
        )
