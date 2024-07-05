from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from api.models import UserAPIKey


@login_required
def authenticate_cli(request):
    """Create an API key for the current user and forward to 'redirect' URL."""
    # Read values from query parameters
    name = request.GET.get("name")
    callback = request.GET.get("callback")

    api_key, key = UserAPIKey.objects.create_key(
        name=name, username=request.user.username
    )
    callback_with_key = f"{callback}?key={key}"
    return HttpResponseRedirect(callback_with_key)
