import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


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
    payment_link = stripe.PaymentLink.create(
        line_items=[{"price": price, "quantity": int(credits)}],
        after_completion={
            "type": "redirect",
            "redirect": {"url": f"{settings.BASE_URL}/dashboard/tasks/"},
        },
        metadata={
            "github_user": request.user.username,
            "credits": int(credits),
        },
    )

    return HttpResponseRedirect(payment_link.url)
