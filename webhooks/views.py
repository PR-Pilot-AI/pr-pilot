import hashlib
import hmac
import json
import logging
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
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


@csrf_exempt
def create_stripe_payment_link(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('account_login'))

    stripe.api_key = settings.STRIPE_API_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Credits Refill',
                },
                'unit_amount': 100,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/') + '?success=true',
        cancel_url=request.build_absolute_uri('/') + '?canceled=true',
        metadata={'user_id': request.user.id},
    )
    return HttpResponseRedirect(session.url)