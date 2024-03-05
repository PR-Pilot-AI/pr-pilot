import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt

from webhooks.handlers.app_deletion import handle_app_deletion
from webhooks.handlers.app_installation import handle_app_installation
from webhooks.handlers.handle_issue_comment import handle_issue_comment
from webhooks.models import GitHubAppInstallation, GitHubAccount


logger = logging.getLogger(__name__)


def is_valid_signature(request):
    github_signature = request.headers.get('X-Hub-Signature-256')
    if not github_signature:
        return False
    signature = 'sha256=' + hmac.new(
        bytes(settings.GITHUB_WEBHOOK_SECRET, 'utf-8'),
        msg=request.body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(github_signature, signature)


@csrf_exempt
def github_webhook(request):
    if not is_valid_signature(request):
        logger.warning('Invalid signature in webhook request')
        return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=403)

    if request.method == 'POST':
        payload = json.loads(request.body.decode('utf-8'))
        event = request.headers.get('X-GitHub-Event', 'ping')  # Get the event type

        if event == 'issue_comment' and payload['action'] == 'created':
            # Handle new issue comment here
            return handle_issue_comment(payload)

        elif event == 'installation' and payload['action'] == 'created':
            # Handle app installation here
            return handle_app_installation(payload)

        elif event == 'installation' and payload['action'] == 'deleted':
            # Handle app deletion here
            return handle_app_deletion(payload)

        else:
            logger.info(f'Received unhandled event: {event}')
            return JsonResponse({'status': 'ignored', 'message': 'Unhandled event'})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
