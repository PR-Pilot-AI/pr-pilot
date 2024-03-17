"""
URL configuration for prpilot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.socialaccount.providers.github.views import oauth2_login
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from accounts.views import health_check, home

urlpatterns = [
    path('admin', admin.site.urls),
    # Redirect default account login to GitHub login URL
    path('accounts/login', RedirectView.as_view(url='/accounts/github/login/?process=login', permanent=True)),
    # Include the allauth URLs
    path('accounts', include('allauth.urls')),
    # Explicitly add a path for GitHub OAuth2 login for clarity
    path('accounts/github/login', oauth2_login, name='github_login'),
    path('user', include('accounts.urls')),
    path('webhooks', include('webhooks.urls')),
    path('dashboard', include('dashboard.urls')),
    path('healthz', health_check, name='health_check'),
    path('', home, name='home'),
]
