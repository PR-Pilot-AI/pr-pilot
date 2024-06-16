from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    inline_serializer,
)
from github import Github
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import BaseHasAPIKey
from rest_framework.views import APIView

from api.models import UserAPIKey
from api.serializers import PromptSerializer, TaskSerializer
from engine.models.task import Task, TaskType
from webhooks.jwt_tools import get_installation_access_token
from webhooks.models import GithubRepository

# Number of tasks to show in the task list
TASK_LIST_LIMIT = 10


class HasUserAPIKey(BaseHasAPIKey):
    model = UserAPIKey

class TaskView(APIView):
    permission_classes = [HasUserAPIKey]

    def get(self, request, pk=None):
        api_key = UserAPIKey.objects.get_from_key(request.headers["X-Api-Key"])
        if pk:
            task = Task.objects.get(id=pk)
            if task.github_user != api_key.username:
                return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        else:
            tasks = Task.objects.filter(github_user=api_key.username)
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
