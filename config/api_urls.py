from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request


@api_view(["GET"])
def hello_world(request: Request) -> Response:
    return Response("Go to '/swagger' or '/redoc' for api documentation")


urlpatterns = [
    path("", hello_world, name="hello"),
    path("event/", include("apps.event.urls")),
    path("team/", include("apps.team.urls")),
    path("security-question/", include("apps.security_question.urls")),
]

