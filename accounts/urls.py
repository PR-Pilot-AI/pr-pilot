from django.urls import path

from . import views

urlpatterns = [
    # Other URL patterns...
    path('logout', views.user_logout, name='user_logout'),
]
