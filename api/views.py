from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from api.serializers import PromptSerializer


@api_view(['POST'])
@permission_classes([HasAPIKey])
def create_task(request):
    serializer = PromptSerializer(data=request.data)
    if serializer.is_valid():
        # TODO: Create and schedule new task
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)