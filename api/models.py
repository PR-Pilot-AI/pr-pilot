from django.db import models
from rest_framework_api_key.models import AbstractAPIKey


class UserAPIKey(AbstractAPIKey):
    username = models.CharField(max_length=200, null=False, blank=False)
    github_project = models.CharField(max_length=200, null=True, blank=True)

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
