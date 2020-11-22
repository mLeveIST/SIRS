from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from django.http import HttpResponse


def authenticated_user(request):
    user = request.user
    if not user.is_authenticated:
        raise PermissionDenied("Not authenticated. Please login before using this request.")
    return user


def requests_to_django(response):
    r = HttpResponse(
        content=response.content,
        status=response.status_code
    )

    for header, value in response.headers.items():
        r[header] = value

    return r
