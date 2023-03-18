from datetime import datetime
from tempfile import NamedTemporaryFile

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.feedback.models import Feedback
from apps.feedback.serializers import FeedbackSerializer
from apps.feedback.services import FeedbackExportService


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Create feedback",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["content"],
            properties={
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="max length 는 500 입니다"
                )
            },
        ),
        responses={201: openapi.Response("created", FeedbackSerializer)},
    ),
)
class FeedbackCreateView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class FeedbackDownloadView(APIView):
    def get(self, request: Request, format=None) -> HttpResponse:
        service = FeedbackExportService()

        wb = service.export_feedbacks()

        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()

        response = HttpResponse(
            content=stream,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            status=204,
        )
        response.headers[
            "Content-Disposition"
        ] = f'attachment; filename="BisTime-Feedbacks-{datetime.now().strftime("%Y%m%d%H%M")}.xlsx'

        return response
