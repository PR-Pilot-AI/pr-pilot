import logging
import re

from django.http import JsonResponse

from engine.tasks.github_issue_task import GithubIssueTask

logger = logging.getLogger(__name__)


def handle_issue_comment(payload: dict):
    # Extract commenter's username
    commenter_username = payload['comment']['user']['login']
    # Extract comment text
    comment_text = payload['comment']['body']

    # Look for slash command pattern
    match = re.search(r'/pilot\s+(.+)', comment_text)

    # If a slash command is found, extract the command
    if match:
        command = match.group(1)
        logger.info(f'Found command: {command} by {commenter_username}')
        task = GithubIssueTask(payload)
        task.pilot_command = command
        task.save()
        task.schedule()

    return JsonResponse({'status': 'ok', 'message': 'Issue comment processed'})
