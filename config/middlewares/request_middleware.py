from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.conf import settings

from config.renderer import CustomRenderer


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.VALID_URLS = ["api", "swagger", "redoc"]

    def __call__(self, request):
        try:
            self.process_request(request)
        except ValidationError as e:
            response = Response(
                {"detail": e.detail[0]}, status=status.HTTP_400_BAD_REQUEST
            )
            response.accepted_renderer = CustomRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}
            response.render()
            return response

        response = self.get_response(request)

        return response

    def process_request(self, request):
        if not settings.DEBUG:
            # deployment environment
            if "api" not in request.path:
                raise ValidationError("all paths should start with '/api'")
            else:
                if (
                    "swagger" not in request.path
                    and len(request.headers["Accept"].split(";")) < 2
                ):
                    raise ValidationError(
                        "Accept header must be 'application/json; version=1;'"
                    )
        else:
            if "api" in request.path and request.path.split("/")[2] not in [
                "swagger",
                "redoc",
                "silk",
                "admin",
            ]:
                if len(request.headers["Accept"].split(";")) < 2:
                    raise ValidationError(
                        "Accept header must be 'application/json; version=1;'"
                    )
