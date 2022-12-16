from django.http import HttpResponse
from django.urls import re_path, include, path


def health_check_view(request):
    return HttpResponse(status=200)


urlpatterns = [
    path("health-check", health_check_view, name="health-check"),
    re_path(r"^api/", include("config.urls_v1")),
]