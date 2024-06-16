from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from . import views

urlpatterns = [
    path("tasks/", views.create_task, name="create_task", methods=['POST']),
    path("tasks/", views.list_tasks, name="list_tasks", methods=['GET']),
    path("tasks/<uuid:pk>/", views.get_task, name="get_task"),
    path("openapi.yaml", SpectacularAPIView.as_view(), name="schema"),
]