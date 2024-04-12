from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import BaseHasAPIKey

from api.models import UserAPIKey
from api.serializers import PromptSerializer, TaskSerializer
from engine.models.task import Task, TaskType
from webhooks.models import GithubRepository


class HasUserAPIKey(BaseHasAPIKey):
    model = UserAPIKey


@api_view(['POST'])
@permission_classes([HasUserAPIKey])
def create_task(request):
    api_key = UserAPIKey.objects.get_from_key(request.headers['X-Api-Key'])
    serializer = PromptSerializer(data=request.data)
    if serializer.is_valid():
        github_user = api_key.username
        try:
            repo = GithubRepository.objects.get(full_name=serializer.validated_data['github_repo'])
        except GithubRepository.DoesNotExist:
            return Response({'error': 'PR Pilot is not installed for this repository'},
                            status=status.HTTP_404_NOT_FOUND)

        task = Task.objects.create(title="A title", user_request=serializer.validated_data['prompt'],
                                   installation_id=repo.installation.installation_id, github_project=repo.full_name,
                                   task_type=TaskType.STANDALONE.value,
                                   github_user=github_user)
        task.schedule()
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)