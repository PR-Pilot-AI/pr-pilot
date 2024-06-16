from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from .views import TaskView

urlpatterns = [
    path("tasks/", TaskView.as_view(), name="task-list-or-create"),
    path("tasks/<uuid:pk>/", TaskView.as_view(), name="task-detail"),
    path("openapi.yaml", SpectacularAPIView.as_view(), name="schema"),
]