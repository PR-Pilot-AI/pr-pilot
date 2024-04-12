import logging

from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

from webhooks.models import GitHubAppInstallation, GitHubAccount, GithubRepository


logger = logging.getLogger(__name__)


def handle_app_installation_change(payload: dict):
    installation = GitHubAppInstallation.objects.get(installation_id=payload['installation']['id'])
    if not installation:
        logger.error(f'Installation not found: {payload["installation"]["id"]}')
        return JsonResponse({'status': 'error', 'message': 'Installation not found'}, status=404)
    for repository in payload['repositories_removed']:
        try:
            repo = GithubRepository.objects.get(id=repository['id'])
            repo.delete()
            logger.info(f'Repository {repo.full_name} removed from installation {installation.installation_id}')
        except GithubRepository.DoesNotExist:
            logger.error(f'Tried to delete repository {repository["full_name"]}, but not found')
            return JsonResponse({'status': 'error', 'message': 'Repository not found'}, status=404)
    for repository in payload['repositories_added']:
        logger.info(f'Repository {repository["full_name"]} added to installation {installation.installation_id}')
        GithubRepository.objects.update_or_create(
            id=repository['id'],
            defaults={
                'full_name': repository['full_name'],
                'name': repository['name'],
                'installation': installation,
            }
        )
    return JsonResponse({'status': 'success', 'installation_id': installation.installation_id})