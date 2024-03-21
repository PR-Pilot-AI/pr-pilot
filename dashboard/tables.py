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

    def render_action(self, record):
        color = 'primary' if not record.reversed else 'danger'
        return format_html('<span class="badge bg-{}">{}</span>', color, record.action.replace('_', ' '))

    class Meta:
        model = TaskEvent  # Use the model associated with the events
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-striped table-hover"}
        fields = ['timestamp', 'action', 'target', 'message']


class EventUndoTable(tables.Table):
    message = MarkdownColumn()

    def render_action(self, record):
        color = 'primary' if not record.reversed else 'danger'
        if record.action in ['close_pull_request', 'close_issue']:
            color = 'warning'
        return format_html('<span class="badge bg-{}">{}</span>', color, record.action.replace('_', ' '))

    def render_reversible(self, record):
        """Render a checkbox column for reversible actions."""
        if record.reversible and not record.reversed:
            return format_html('<input type="checkbox" name="reversible" value="{}" checked>', record.id)
        else:
            return format_html('<input type="checkbox" name="reversible" value="{}" disabled>', record.id)


    class Meta:
        model = TaskEvent  # Use the model associated with the events
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-striped table-hover"}
        fields = ['reversible', 'timestamp', 'action', 'target', 'message']



class CostItemTable(tables.Table):

    def render_model_name(self, value):
        return format_html('<span class="badge bg-secondary">{}</span>', value)

    def render_credits(self, value):
        usd_string = '{:.1f}'.format(value)
        return usd_string

    class Meta:
        model = CostItem
        template_name = "django_tables2/bootstrap5.html"
        fields = ['title', 'model_name', 'credits']