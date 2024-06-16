from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from . import views

urlpatterns = [
    path("tasks/", views.TaskViewSet.as_view()),
    path("tasks/<uuid:pk>/", views.get_task, name="get_task"),
    path("openapi.yaml", SpectacularAPIView.as_view(), name="schema"),
]
