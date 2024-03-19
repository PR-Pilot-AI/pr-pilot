import hashlib
import hmac
import json
import logging
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from accounts.models import UserBudget
from webhooks.handlers.app_deletion import handle_app_deletion
from webhooks.handlers.app_installation import handle_app_installation
from webhooks.handlers.handle_issue_comment import handle_issue_comment
from webhooks.handlers.pull_request_review_comment import handle_pull_request_review_comment

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
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f'Invalid payload: {e}')
        return JsonResponse({'status': 'error', 'message': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f'Invalid signature: {e}')
        return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        github_user = session.metadata['github_user']
        credit_count = session.metadata['credits']
        budget = UserBudget.get_user_budget(github_user)
        budget.budget += Decimal(f'{credit_count}.00')
        budget.save()
        logger.info(f'Payment completed for user {github_user}')
        logger.info(f'Added {credit_count} credits. New budget: {budget.budget}')
        return JsonResponse({'status': 'success', 'message': 'Payment registered'}, status=200)

    return JsonResponse({'status': 'ignored', 'message': 'Unhandled event'})


@csrf_exempt
def github_webhook(request):
    if not is_valid_signature(request):
        logger.warning('Invalid signature in webhook request')
        return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=403)

    if request.method == 'POST':
        payload = json.loads(request.body.decode('utf-8'))
        event = request.headers.get('X-GitHub-Event', 'ping')  # Get the event type

        if event == 'pull_request_review_comment' and payload['action'] == 'created':
            # Handle new pull request review comment here
            return handle_pull_request_review_comment(payload)

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
