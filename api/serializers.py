from rest_framework import serializers

from engine.models.task import Task


class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, allow_blank=False, help_text="The prompt for the task")
    github_repo = serializers.CharField(required=True, allow_blank=False, help_text="The full name of the Github repository, e.g. 'owner/repo'")


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'user_request', 'github_project', 'github_user', 'status', 'created', 'result']