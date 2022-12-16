from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from config.renderer import CustomRenderer


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.VALID_URLS = [
            "/api", "/swagger", "/redoc"
        ]

    def __call__(self, request):

        try:
            self.process_request(request)
        except ValidationError as e:
            response = Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
            response.accepted_renderer = CustomRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}
            response.render()
            return response

        response = self.get_response(request)

        return response

    def process_request(self, request):
        if request.headers["Accept"].split(";")[1] == "":
            raise ValidationError("Accept header must include api version")

        if request.path not in self.VALID_URLS:
            raise ValidationError({"detail": "all urls must include /api except api document url"})
