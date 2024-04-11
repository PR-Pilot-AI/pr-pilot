from django.contrib import admin

from engine.models.cost_item import CostItem
from engine.models.task import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'issue_number', 'comment_id', 'github_project', 'github_user', 'branch', 'created', 'status')  # Specify the fields to display
    search_fields = ['title', 'user_request', 'issue_number', 'comment_id', ]  # Specify fields to search in
    list_filter = ('github_project', 'pr_number', 'issue_number', 'github_project', 'status')  # Specify fields to filter by

class CostItemAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'model_name', 'title', 'total_cost_usd')  # Specify the fields to display
    search_fields = ['title', 'model_name']  # Specify fields to search in
    list_filter = ('model_name', 'timestamp')  # Specify fields to filter by


# Register your models here.
admin.site.register(Task, TaskAdmin)
admin.site.register(CostItem, CostItemAdmin)