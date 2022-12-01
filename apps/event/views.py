from typing import Any

from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.request import Request

from apps.event.models import Event, EventDate, Schedule
from apps.event.serializers import (
    EventSerializer,
    EventDateSerializer,
    ScheduleSerializer,
)
from apps.event.services import EventService


class EventCreateView(generics.CreateAPIView):

    serializer_class = EventSerializer
    queryset = Event.objects.all()

    @swagger_auto_schema(
        operation_summary="Create a new instant event",
        responses={
            201: openapi.Response("Success", EventSerializer),
            400: "Validation error",
        },
        request_body=openapi.Schema(
            required=["title", "start_time", "end_time"],
            type=openapi.TYPE_OBJECT,
            properties={
                "associated_team": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="연관된 팀"
                ),
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="제목"),
                "start_time": openapi.Schema(
                    type=openapi.TYPE_STRING, description="시간 범위의 시작점"
                ),
                "end_time": openapi.Schema(
                    type=openapi.TYPE_STRING, description="시간 범위의 끝점"
                ),
            },
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(uuid=EventService.generate_uuid())

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventUpdateView(generics.UpdateAPIView):
    """
    Update an instant event
    """

    serializer_class = EventSerializer
    queryset = Event.objects.all()
    allowed_methods = ["PATCH"]

    @swagger_auto_schema(
        operation_summary="Update an instant event",
        operation_description="only updates start_time, end_time, and adds available date",
        responses={
            200: openapi.Response("Success", EventSerializer),
            400: "Validation error",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "associated_team": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="연관된 팀"
                ),
                "start_time": openapi.Schema(
                    type=openapi.TYPE_STRING, description="시간 범위의 시작점"
                ),
                "end_time": openapi.Schema(
                    type=openapi.TYPE_STRING, description="시간 범위의 끝점"
                ),
            },
        ),
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass


class EventDateView(generics.UpdateAPIView):
    """
    Update dates for instant event
    """

    serializer_class = EventDateSerializer
    queryset = EventDate.objects.all()
    allowed_methods = ["PATCH"]

    @swagger_auto_schema(
        operation_summary="Update an instant event's date",
        operation_description="only adds additional dates, deletion not allowed",
        responses={
            200: openapi.Response("Success", EventDateSerializer),
            400: "Validation error",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "additional_dates": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.FORMAT_DATE),
                    description="추가할 날짜 리스트",
                )
            },
        ),
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Add user's schedule to an event by name",
        responses={201: openapi.Response("Success", ScheduleSerializer)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="유저 이름"),
                "event": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="연관된 Event 모델의 ID"
                ),
                "date": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="연관된 EventDate 모델의 ID"
                ),
                "availability": openapi.Schema(
                    type=openapi.FORMAT_BINARY,
                    description="하루를 48등분 (30분 단위) 하여 Blob 형태로 전달",
                ),
            },
        ),
    ),
)
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Fetch all data associated with a single instant event",
        responses={200: openapi.Response("Success", ScheduleSerializer)},
    ),
)
class ScheduleList(generics.ListCreateAPIView):
    """
    Lists all schedules associated with an event and creates a schedule
    """

    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()


class ScheduleDetail(generics.UpdateAPIView):
    """
    Updates a member's schedule associated with a certain date
    """

    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()
    allowed_methods = ["PATCH"]

    @swagger_auto_schema(
        operation_summary="Update a member's schedule associated with a certain date",
        responses={
            200: openapi.Response("Success", ScheduleSerializer),
            400: "Validation error",
        },
        request_body=ScheduleSerializer,
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass
