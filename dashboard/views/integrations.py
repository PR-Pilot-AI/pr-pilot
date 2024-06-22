import logging

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from accounts.models import SlackIntegration, LinearIntegration, SentryIntegration, UserBudget
from engine.cryptography import encrypt


logger = logging.getLogger(__name__)


@login_required
def add_slack_integration(request):
    """Callback for Slack Oauth flow."""
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("account_login"))

    code = request.GET.get("code")
    if not code:
        HttpResponse("Missing 'code' query parameter", status=400)

    # Exchange the code for an access token
    redirect_path = reverse("add_slack_integration")
    scheme = "https" if request.is_secure() else "http"
    domain = request.get_host()
    full_url = f"{scheme}://{domain}{redirect_path}"
    response = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "code": code,
            "client_id": settings.SLACK_CLIENT_ID,
            "client_secret": settings.SLACK_CLIENT_SECRET,
            "redirect_uri": full_url,
        },
    )

    if response.status_code != 200:
        HttpResponse(
            f"Failed to finish Slack integration: {str(response)} ",
            status=response.status_code,
        )

    json_response = response.json()
    if not json_response.get("ok"):
        return HttpResponse(f"Error: {json_response.get('error')}", 400)

    # Create a new Slack integration for the user
    bot_token = encrypt(json_response["access_token"])
    user_token = encrypt(json_response["authed_user"]["access_token"])

    logger.info(f"Creating Slack integration for user {request.user.username}")
    if not request.user.slack_integration:
        request.user.slack_integration = SlackIntegration.objects.create(
            bot_token=bot_token, user_token=user_token
        )
        request.user.save()
    else:
        request.user.slack_integration.bot_token = bot_token
        request.user.slack_integration.user_token = user_token
        request.user.slack_integration.save()

    # Redirect to the integrations page
    return redirect("integrations")


@login_required
def add_linear_integration(request):
    """Callback for Linear Oauth flow."""
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("account_login"))

    code = request.GET.get("code")
    if not code:
        HttpResponse("Missing 'code' query parameter", status=400)

    # Exchange the code for an access token
    redirect_path = reverse("add_linear_integration")
    scheme = "https" if request.is_secure() else "http"
    domain = request.get_host()
    full_url = f"{scheme}://{domain}{redirect_path}"
    response = requests.post(
        "https://api.linear.app/oauth/token",
        data={
            "code": code,
            "client_id": settings.LINEAR_CLIENT_ID,
            "client_secret": settings.LINEAR_CLIENT_SECRET,
            "redirect_uri": full_url,
            "grant_type": "authorization_code",
        },
    )

    if response.status_code != 200:
        HttpResponse(
            f"Failed to finish Linear integration: {str(response)} ",
            status=response.status_code,
        )

    json_response = response.json()
    if not response.ok:
        return HttpResponse(f"Error: {json_response.get('error')}", 400)

    # Create a new Linear integration for the user
    access_token = encrypt(json_response["access_token"])

    logger.info(f"Creating Linear integration for user {request.user.username}")
    if not request.user.linear_integration:
        request.user.linear_integration = LinearIntegration.objects.create(
            access_token=access_token
        )
        request.user.save()
    else:
        request.user.linear_integration.access_token = access_token
        request.user.linear_integration.save()

    # Redirect to the integrations page
    return redirect("integrations")


class IntegrationView(LoginRequiredMixin, TemplateView):
    template_name = "integrations.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        budget = UserBudget.get_user_budget(self.request.user.username)
        context["budget"] = budget.formatted
        context["slack_bot_token"] = (
            self.request.user.slack_integration.bot_token
            if self.request.user.slack_integration
            else None
        )
        context["linear_access_token"] = (
            self.request.user.linear_integration.access_token
            if self.request.user.linear_integration
            else None
        )
        context["sentry_api_key"] = (
            self.request.user.sentry_integration.api_key
            if self.request.user.sentry_integration
            else None
        )
        context["site_host"] = self.request.get_host()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "delete_slack_integration":
            logger.info(f"Deleting Slack integration for user {request.user.username}")
            # Delete the Slack API key from the user's profile
            request.user.slack_integration.bot_token = None
            request.user.slack_integration.save()
        elif action == "delete_linear_integration":
            logger.info(f"Deleting Linear integration for user {request.user.username}")
            # Delete the Linear API key from the user's profile
            request.user.linear_integration.access_token = None
            request.user.linear_integration.save()
        elif action == "delete_sentry_integration":
            logger.info(f"Deleting Sentry integration for user {request.user.username}")
            # Delete the Sentry API key from the user's profile
            request.user.sentry_integration.api_key = None
            request.user.sentry_integration.save()
        elif "sentry_api_key" in request.POST:
            api_key = request.POST.get("sentry_api_key")
            logger.info(f"Adding Sentry integration for user {request.user.username}")
            if not request.user.sentry_integration:
                request.user.sentry_integration = SentryIntegration.objects.create(api_key=api_key)
                request.user.save()
            else:
                request.user.sentry_integration.api_key = api_key
                request.user.sentry_integration.save()
        return redirect("integrations")
