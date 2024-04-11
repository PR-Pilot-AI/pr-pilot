import logging

from github import Github

from engine.models import Task
from webhooks.jwt_tools import get_installation_access_token

logger = logging.getLogger(__name__)


class GithubIssueTask(Task):
    """A task that was triggered by a comment on a Github issue"""

    class Meta:
        proxy = True

    def __init__(self, payload, **kwargs):
        super().__init__(**kwargs)
        self.comment_id = payload['comment']['id']
        self.comment_url = payload['comment']['html_url']
        self.github_user = payload['comment']['user']['login']
        self.issue_number = payload['issue']['number']
        self.github_project = payload['repository']['full_name']
        self.installation_id = payload['installation']['id']
        comment_text = payload['comment']['body']

        g = Github(get_installation_access_token(self.installation_id))
        repo = g.get_repo(self.github_project)
        issue = repo.get_issue(number=self.issue_number)
        comment = issue.get_comment(self.comment_id)
        comment.create_reaction("eyes")
        issue_or_pr = "PR" if issue.pull_request else "Issue"
        self.user_request = f"""
The Github user `{self.github_user}` mentioned you in a comment:

{issue_or_pr} number: {self.issue_number}
User comment:
```
{comment_text}
```

Read the {issue_or_pr}, fulfill the user's request and return your response to the user's comment.
"""
        self.title = f"Respond to {issue_or_pr} #{self.issue_number} in {self.github_project}"
        self.branch = repo.default_branch

        if issue.pull_request:
            pr = repo.get_pull(self.issue_number)
            self.pr_number = self.issue_number
            self.head = pr.head.ref
            self.base = pr.base.ref

    def respond_to_user(self, message):
        """Respond to the user's comment on the issue"""
        repo = self.github.get_repo(self.github_project)
        issue = repo.get_issue(self.issue_number)
        comment = issue.create_comment(message)
        self.response_comment_id = comment.id
        self.response_comment_url = comment.html_url
        self.save()

    def acknowledge_user_prompt(self):
        """Replace `/pilot <command>` with `**/pilot** <link_to_task>` in the user's comment"""
        replaced = self.request_comment.body.replace(f"/pilot", f"**/pilot**")
        replaced = replaced.replace(f"{self.pilot_command}",
                                    f"[{self.pilot_command}](https://app.pr-pilot.ai/dashboard/tasks/{str(self.id)}/)")
        self.request_comment.edit(replaced)

