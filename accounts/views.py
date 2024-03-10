from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect


@login_required
def user_logout(request):
    # Log out the user
    logout(request)
    # Redirect to home page (or any other page you prefer)
    return redirect('/')


def home(request):
    if request.user.is_authenticated:
        # Redirect to dashboard
        return redirect('task_list')
    else:
        return render(request, 'home.html')


def health_check(request):
    return HttpResponse("OK")