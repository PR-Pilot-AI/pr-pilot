import logging

from django.http import JsonResponse

from api.models import UserAPIKey
from webhooks.models import GitHubAppInstallation


logger = logging.getLogger(__name__)

def handle_app_deletion(payload):
    app_id = payload['installation']['app_id']
    logger.info(f'Uninstalling app {app_id}')
    GitHubAppInstallation.objects.filter(installation_id=payload['installation']['id']).delete()

    github_user = payload['installation']['account']['login']

    # Delete API keys for all repositories of this installation
    for repo in payload['repositories']:
        logger.info(f'Deleting API keys for repository {repo["full_name"]}')
        UserAPIKey.objects.filter(github_project=repo['full_name'], username=github_user).delete()

    return JsonResponse({'status': 'success', 'message': 'Installation deleted'})