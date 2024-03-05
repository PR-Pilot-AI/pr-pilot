import logging
import re

from django.http import JsonResponse
from github import Github

from engine.models import Task
from webhooks.jwt_tools import get_installation_access_token

logger = logging.getLogger(__name__)


def handle_issue_comment(payload: dict):
    # Extract commenter's username
    commenter_username = payload['comment']['user']['login']
    issue_number = payload['issue']['number']
    comment_id = payload['comment']['id']
    repository = payload['repository']['full_name']
    installation_id = payload['installation']['id']

    # Extract comment text
    comment_text = payload['comment']['body']

    # Look for slash command pattern
    match = re.search(r'/pilot\s+(.+)', comment_text)

    # If a slash command is found, extract the command
    if match:
        command = match.group(1)
        logger.info(f'Found command: {command} by {commenter_username}')
        g = Github(get_installation_access_token(installation_id))
        repo = g.get_repo(repository)
        issue = repo.get_issue(number=issue_number)
        comment = issue.get_comment(comment_id)
        comment.create_reaction("eyes")
        user_request = f"""
The Github user `{commenter_username}` mentioned you in a comment:

Issue number: {issue_number}
User comment:
```
{command}
```

Read the issue, fulfill the user's request and return the response to the user's comment.
"""
        Task.schedule(title="Respond to comment", user_request=user_request,
                      issue_number=issue_number, comment_id=comment_id,
                      installation_id=installation_id, github_project=repository,
                      github_user=commenter_username, branch="main")

    else:
        command = None

    return JsonResponse({'status': 'ok', 'message': 'Issue comment processed'})
