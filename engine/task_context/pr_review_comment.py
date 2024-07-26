from engine.models.task_event import TaskEvent
from engine.task_context.task_context import TaskContext


class PRReviewCommentContext(TaskContext):
    """A task was triggered by a comment on a PR Review"""

    def acknowledge_user_prompt(self):
        """Replace `/pilot <command>` with `**/pilot** <link_to_task>` in the user's comment"""
        replaced = self.task.request_comment.body.replace("/pilot", "**/pilot**")
        replaced = replaced.replace(
            f"{self.task.pilot_command}",
            f"[{self.task.pilot_command}](https://app.pr-pilot.ai/dashboard/tasks/{str(self.task.id)}/)",
        )
        self.task.request_comment.edit(replaced)

    def respond_to_user(self, message):
        """Respond to the user's comment on the issue"""
        repo = self.task.github.get_repo(self.task.github_project)
        pr = repo.get_pull(self.task.pr_number)
        comment = pr.create_review_comment_reply(self.task.comment_id, message)
        self.task.response_comment_id = comment.id
        self.task.response_comment_url = comment.html_url
        self.task.save()
        TaskEvent.add(
            actor="assistant",
            action="comment_on_issue",
            target=comment.id,
            message=f"Comment on [PR #{self.task.pr_number}]({comment.html_url})",
        )
