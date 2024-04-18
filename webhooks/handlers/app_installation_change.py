import logging

from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from github import Github

from api.models import UserAPIKey
from webhooks.handlers.util import install_repository, GITHUB_SECRET_NAME, uninstall_repository
from webhooks.jwt_tools import get_installation_access_token
from webhooks.models import GitHubAppInstallation, GitHubAccount, GithubRepository


logger = logging.getLogger(__name__)


def handle_app_installation_change(payload: dict):
    installation = GitHubAppInstallation.objects.get(installation_id=payload['installation']['id'])
    if not installation:
        logger.error(f'Installation not found: {payload["installation"]["id"]}')
        return JsonResponse({'status': 'error', 'message': 'Installation not found'}, status=404)
    for repository in payload['repositories_removed']:
        try:
            uninstall_repository(repository, installation.account.login)
        except GithubRepository.DoesNotExist:
            logger.error(f'Tried to delete repository {repository["full_name"]}, but not found')
            return JsonResponse({'status': 'error', 'message': 'Repository not found'}, status=404)
    for repository in payload['repositories_added']:
        logger.info(f'Repository {repository["full_name"]} added to installation {installation.installation_id}')
        install_repository(installation, repository, installation.account.login)
    return JsonResponse({'status': 'success', 'installation_id': installation.installation_id})