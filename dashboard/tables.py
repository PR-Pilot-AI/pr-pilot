import markdown
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_tables2 import tables, A

from engine.models import Task, TaskEvent, CostItem


class GithubProjectLinkColumn(tables.columns.Column):

    def render(self, value):
        return format_html('<a href="https://github.com/{}" target="_blank">{}</a>', value, value)


class TaskStatusColumn(tables.columns.Column):

        def render(self, value):
            color = 'success'
            if value == 'scheduled':
                color = 'primary'
            elif value == 'running':
                color = 'warning'
            elif value == 'failed':
                color = 'danger'
            return format_html('<span class="badge bg-{}">{}</span>', color, value)


class MarkdownColumn(tables.columns.Column):
    def render(self, value):
        # Convert Markdown to HTML and mark it safe for rendering
        return mark_safe(markdown.markdown(value))


class TaskTable(tables.Table):
    title = tables.columns.RelatedLinkColumn("task_detail", args=[A("pk")])
    github_project = GithubProjectLinkColumn()
    status = TaskStatusColumn()


    def render_title(self, value):
        # Truncate the title to 50 characters
        return value[:50] + '...' if len(value) > 50 else value

    def render_issue_number(self, record):
        issue_number = record.issue_number if record.issue_number else record.pr_number
        return format_html(f'<a href="{record.comment_url}" target="_blank">#{issue_number}</a>')

    class Meta:
        model = Task
        order_by = ('-created',)
        template_name = "django_tables2/bootstrap5.html"
        fields = ("created", "title", "status", "github_project", "issue_number")

class EventTable(tables.Table):
    message = MarkdownColumn()

    def render_target(self, record):
        github_issue_targets = ['create_github_issue', 'close_github_issue', 'read_github_issue', 'edit_github_issue', 'close_pull_request', 'read_pull_request', 'create_pull_request']
        if record.action in github_issue_targets:
            issue_url = f"https://github.com/{record.task.github_project}/issues/{record.target}"
            return format_html('<a href="{}" target="_blank">#{}</a>', issue_url, record.target)
        elif record.action == 'clone_repo':
            repo_url = f"https://github.com/{record.task.github_project}"
            return format_html('<a href="{}" target="_blank">{}</a>', repo_url, record.target)
        elif record.action == 'commit_changes':
            commit_url = f"https://github.com/{record.task.github_project}/commit/{record.target}"
            return format_html('<a href="{}" target="_blank">{}</a>', commit_url, record.target)
        elif record.action in ['push_branch', 'checkout_pr_branch']:
            branch_url = f"https://github.com/{record.task.github_project}/tree/{record.target}"
            return format_html('<a href="{}" target="_blank">{}</a>', branch_url, record.target)
        elif record.action == 'comment_on_issue':
            issue_id = record.task.pr_number if record.task.pr_number else record.task.issue_number
            return format_html('<a href="{}" target="_blank">#{}</a>', record.task.response_comment_url, issue_id)
        else:
            return record.target

    def render_action(self, record):
        color = 'primary' if not record.reversed else 'danger'
        if record.action in ['close_pull_request', 'close_github_issue', 'delete_github_comment']:
            color = 'warning'
        return format_html('<span class="badge bg-{}">{}</span>', color, record.action.replace('_', ' '))

    class Meta:
        model = TaskEvent  # Use the model associated with the events
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-striped table-hover"}
        fields = ['action', 'target', 'message']


class EventUndoTable(EventTable):
    message = MarkdownColumn()

    def render_reversible(self, record):
        """Render a checkbox column for reversible actions."""
        if record.reversible and not record.reversed:
            return format_html('<input type="checkbox" name="reversible" value="{}" checked>', record.id)
        else:
            return format_html('<input type="checkbox" name="reversible" value="{}" disabled>', record.id)


    class Meta(EventTable.Meta):
        fields = ['reversible', 'action', 'target', 'message']


class CostItemTable(tables.Table):

    def render_title(self, value):
        return format_html('<span class="lead">{}</span>', value.replace('_', ' '))

    def render_model_name(self, value):
        return format_html('<span class="badge bg-secondary">{}</span>', value)

    def render_credits(self, value):
        usd_string = '{:.1f}'.format(value)
        return format_html('<span class="badge rounded-pill bg-dark"><i class="fa-solid fa-coins"></i> {}</span>', usd_string)

    class Meta:
        model = CostItem
        template_name = "django_tables2/bootstrap5.html"
        fields = ['credits', 'title', 'model_name']