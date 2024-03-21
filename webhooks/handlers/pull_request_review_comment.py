import logging
import re

from django.http import JsonResponse
from github import Github

from accounts.models import PilotUser, UserBudget
from engine.models import Task
from webhooks.jwt_tools import get_installation_access_token

logger = logging.getLogger(__name__)


def handle_pull_request_review_comment(payload):
    # Extract commenter's username
    commenter_username = payload['comment']['user']['login']
    comment_id = payload['comment']['id']
    comment_url = payload['comment']['html_url']
    pr_number = payload['pull_request']['number']
    head = payload['pull_request']['head']['ref']
    base = payload['pull_request']['base']['ref']
    repository = payload['repository']['full_name']
    installation_id = payload['installation']['id']
    diff = payload['comment']['diff_hunk']

    # Extract comment text
    comment_text = payload['comment']['body']

    # Look for slash command pattern
    match = re.search(r'/pilot\s+(.+)', comment_text)

    # If a slash command is found, extract the command
    if match:
        budget = UserBudget.get_user_budget(commenter_username)
        command = match.group(1)
        logger.info(f'Found command: {command} by {commenter_username}')
        g = Github(get_installation_access_token(installation_id))
        repo = g.get_repo(repository)
        pr = repo.get_pull(pr_number)
        comment = repo.get_pull(pr_number).get_comment(comment_id)
        UserBudget.objects.get(username=commenter_username)
        if budget.budget <= 0:
            logger.info(f'User {commenter_username} has no budget')
            pr.create_review_comment_reply(comment_id, "You have used up your budget. Please visit the [Dashboard](https://app.pr-pilot.ai) to purchase more credits.")
            return JsonResponse({'status': 'ok', 'message': 'PR comment processed'})
        comment.create_reaction("eyes")
        user_request = f"""
    The Github user `{commenter_username}` mentioned you in a comment on a pull request review:
    PR number: {pr_number}
    
    Diff hunk:
    ```
    {diff}
    ```
    
    User Comment:
    ```
    {comment_text}
    ```

    Read the pull request, fulfill the user's request and return the response to the user's comment.
    """
        Task.schedule(title=command, user_request=user_request, comment_id=comment_id,
                      comment_url=comment_url, pr_number=pr_number, head=head, base=base,
                      installation_id=installation_id, github_project=repository,
                      github_user=commenter_username, branch="main", pilot_command=command)

    else:
        command = None

    return JsonResponse({'status': 'ok', 'message': 'PR comment processed'})
