from rest_framework import generics
from .models import Task
from .serializers import TaskSerializer

class TaskListView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
