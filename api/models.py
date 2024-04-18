from django.db import models
from rest_framework_api_key.models import AbstractAPIKey

from accounts.models import PilotUser


class UserAPIKey(AbstractAPIKey):
    username = models.CharField(max_length=200, null=False, blank=False)
    github_project = models.CharField(max_length=200, null=True, blank=True)
