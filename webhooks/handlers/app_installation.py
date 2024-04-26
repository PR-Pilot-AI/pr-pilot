import logging

from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

from webhooks.handlers.util import install_repository
from webhooks.models import GitHubAppInstallation, GitHubAccount

logger = logging.getLogger(__name__)


def handle_app_installation(payload: dict):
    # Parse account data
    account_data = payload["installation"]["account"]
    account, _ = GitHubAccount.objects.get_or_create(
        account_id=account_data["id"],
        defaults={
            "login": account_data["login"],
            "avatar_url": account_data["avatar_url"],
            "html_url": account_data["html_url"],
        },
    )

    # Parse installation data
    installation_data = payload["installation"]
    installation, _ = GitHubAppInstallation.objects.update_or_create(
        installation_id=installation_data["id"],
        app_id=installation_data["app_id"],
        target_id=installation_data["target_id"],
        target_type=installation_data["target_type"],
        defaults={
            "account": account,
            "access_tokens_url": installation_data["access_tokens_url"],
            "repositories_url": installation_data["repositories_url"],
            "installed_at": parse_datetime(installation_data["created_at"]),
        },
    )
    repositories_data = payload["repositories"]
    github_user = payload["sender"]["login"]
    for repo_data in repositories_data:
        logger.info(
            f'User {account.login} installed PR Pilot for repository {repo_data["full_name"]}'
        )
        install_repository(installation, repo_data, github_user)

    return JsonResponse(
        {"status": "success", "installation_id": installation.installation_id}
    )
