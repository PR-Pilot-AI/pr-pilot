import logging

from django.http import JsonResponse

from webhooks.handlers.util import (
    install_repository,
    uninstall_repository,
)
from webhooks.models import GitHubAppInstallation, GithubRepository

logger = logging.getLogger(__name__)


def handle_app_installation_change(payload: dict):
    installation = GitHubAppInstallation.objects.get(
        installation_id=payload["installation"]["id"]
    )
    if not installation:
        logger.error(f'Installation not found: {payload["installation"]["id"]}')
        return JsonResponse(
            {"status": "error", "message": "Installation not found"}, status=404
        )
    github_user = payload["sender"]["login"]
    for repository in payload["repositories_removed"]:
        try:
            uninstall_repository(repository, github_user)
        except GithubRepository.DoesNotExist:
            logger.error(
                f'Tried to delete repository {repository["full_name"]}, but not found'
            )
            return JsonResponse(
                {"status": "error", "message": "Repository not found"}, status=404
            )
    for repository in payload["repositories_added"]:
        logger.info(
            f'Repository {repository["full_name"]} added to installation {installation.installation_id}'
        )
        install_repository(installation, repository, github_user)
    return JsonResponse(
        {"status": "success", "installation_id": installation.installation_id}
    )
