from django.contrib import admin

from webhooks.models import GitHubAppInstallation


class GitHubAppInstallationAdmin(admin.ModelAdmin):
    list_display = (
        "installation_id",
        "account__login",
        "installed_at",
        "target_id",
        "target_type",
    )  # Specify the fields to display
    search_fields = ["installation_id"]  # Specify fields to search in
    list_filter = (
        "installed_at",
        "target_type",
    )  # Specify fields to filter by


# Register your models here.
admin.site.register(GitHubAppInstallation)
