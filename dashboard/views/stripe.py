import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

logger = logging.getLogger(__name__)


@login_required
def create_stripe_payment_link(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("account_login"))

    # Get 'credits' query param
    credits = request.GET.get("credits")
    if not credits:
        return HttpResponseRedirect(reverse("task_list"))

    stripe.api_key = settings.STRIPE_API_KEY
    price = (
        "price_1OvuaJCyRBEZZGEuL8I9b308"
        if settings.DEBUG
        else "price_1OwBvgCyRBEZZGEuAbzUzfRF"
    )
    try:
        payment_link = stripe.PaymentLink.create(
            line_items=[{"price": price, "quantity": int(credits)}],
            after_completion={
                "type": "redirect",
                "redirect": {"url": "https://app.pr-pilot.ai/dashboard/tasks/"},
            },
            metadata={
                "github_user": request.user.username,
                "credits": int(credits),
            },
        )
        logger.info(f"Payment link created for user {request.user} requesting {credits} credits")
        return HttpResponseRedirect(payment_link.url)
    except stripe.error.StripeError as e:
        logger.error(f"Payment error for user {request.user}: {e}")
        messages.error(request, f"Payment error: {e.user_message or e.error.message}")
        return HttpResponseRedirect(reverse("task_list"))
