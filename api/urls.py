from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from api import views

urlpatterns = [
    path('tasks/', views.create_task, name='create_task'),
    path('tasks/<uuid:pk>/', views.get_task, name='get_task'),
    path('openapi.yaml', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
