import logging
import re

from django.http import JsonResponse
from github import Github

from engine.models.task import Task, TaskType
from webhooks.jwt_tools import get_installation_access_token

logger = logging.getLogger(__name__)


def handle_pull_request_review_comment(payload):
    # Extract commenter's username
    commenter_username = payload["comment"]["user"]["login"]
    comment_id = payload["comment"]["id"]
    comment_url = payload["comment"]["html_url"]
    pr_number = payload["pull_request"]["number"]
    head = payload["pull_request"]["head"]["ref"]
    base = payload["pull_request"]["base"]["ref"]
    repository = payload["repository"]["full_name"]
    installation_id = payload["installation"]["id"]
    diff = payload["comment"]["diff_hunk"]
    file_path = payload["comment"]["path"]

    # Extract comment text
    comment_text = payload["comment"]["body"]

    # Look for slash command pattern
    match = re.search(r"/pilot\s+(.+)", comment_text)

    # If a slash command is found, extract the command
    if match:
        command = match.group(1)
        logger.info(f"Found command: {command} by {commenter_username}")
        g = Github(get_installation_access_token(installation_id))
        repo = g.get_repo(repository)
        comment = repo.get_pull(pr_number).get_comment(comment_id)
        comment.create_reaction("eyes")
        user_request = f"""
    The Github user `{commenter_username}` mentioned you in a comment on a PR review:
    PR number: {pr_number}

    Diff hunk for `{file_path}`:
    ```
    {diff}
    ```

    User comment on diff:
    ```
    {comment_text}
    ```

    Read the pull request and understand the user's comment in context. If the user asks for changes,
    write those changes directly to the file on which they commented.
    """
        task = Task.objects.create(
            title=command,
            user_request=user_request,
            comment_id=comment_id,
            comment_url=comment_url,
            pr_number=pr_number,
            head=head,
            base=base,
            installation_id=installation_id,
            github_project=repository,
            task_type=TaskType.GITHUB_PR_REVIEW_COMMENT.value,
            github_user=commenter_username,
            branch="main",
            pilot_command=command,
        )
        task.schedule()

    else:
        command = None

    return JsonResponse({"status": "ok", "message": "PR comment processed"})
