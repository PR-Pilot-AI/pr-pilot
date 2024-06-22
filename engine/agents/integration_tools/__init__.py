import logging

from accounts.models import PilotUser
from engine.cryptography import decrypt
from .linear_tools import list_linear_tools
from .slack_tools import list_slack_tools
from .sentry_tools import list_sentry_tools

logger = logging.getLogger(__name__)


def integration_tools_for_user(user: PilotUser):
    tools = []
    if user.linear_integration and user.linear_integration.access_token:
        logger.info(f"User {user.username} has a Linear integration.")
        tools = tools + list_linear_tools(decrypt(user.linear_integration.access_token))
    if user.slack_integration and user.slack_integration.bot_token:
        logger.info(f"User {user.username} has a Slack integration.")
        tools = tools + list_slack_tools(
            decrypt(user.slack_integration.bot_token),
            decrypt(user.slack_integration.user_token),
        )
    if user.sentry_integration and user.sentry_integration.api_key:
        logger.info(f"User {user.username} has a Sentry integration.")
        tools = tools + list_sentry_tools(decrypt(user.sentry_integration.api_key))
    if not tools:
        logger.info(f"User {user.username} has no integrations.")
    return tools
