from rest_framework import serializers

from engine.models.task import Task


class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, allow_blank=False)
    github_repo = serializers.CharField(required=True, allow_blank=False)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'user_request', 'github_project', 'github_user', 'status', 'created', 'result']