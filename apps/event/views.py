from datetime import datetime, date
from typing import Any, List
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.request import Request

from apps.event.models import Event, EventDate, Schedule
from apps.event.serializers import (
    EventSerializer,
    EventDateSerializer,
    ScheduleSerializer,
)
from apps.event.services import EventService
from config.exceptions import InstanceNotFound


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Get all events",
        responses={200: openapi.Response("Success", EventSerializer)},
    ),
)
class EventView(generics.ListCreateAPIView):
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
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    allowed_methods = ["PATCH"]

    @swagger_auto_schema(
        operation_summary="Update an instant event",
        operation_description="only updates start_time, end_time",
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
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_at=datetime.now())

        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Get all dates associated with an event",
        responses={200: openapi.Response("Success", EventDateSerializer)},
    ),
)
class EventDateView(generics.ListCreateAPIView):
    serializer_class = EventDateSerializer
    queryset = EventDate.objects.all()
    allowed_methods = ["POST"]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(event=self.kwargs["pk"])
        return qs

    @swagger_auto_schema(
        operation_summary="Update(Add) an instant event's date",
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
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        additional_dates: List[date] = request.data.get("additional_dates")
        associated_event_id: int = kwargs.get("pk")

        try:
            associated_event: Event = get_object_or_404(Event, id=associated_event_id)
        except Http404:
            raise InstanceNotFound("event with the provided id does not exist")

        associated_dates: List[EventDate] = []

        for d in additional_dates:
            data = {"date": d, "event": associated_event_id}

            serializer = self.get_serializer(data=data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

            associated_dates.append(serializer.data)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Get all schedule data associated with a single instant event",
        responses={200: openapi.Response("Success", ScheduleSerializer)},
    ),
)
class ScheduleList(generics.ListCreateAPIView):
    """
    Lists all schedules associated with an event and creates a schedule
    """

    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()

    @swagger_auto_schema(
        operation_summary="Add user's schedule to an event by name",
        responses={201: openapi.Response("Success", ScheduleSerializer)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="유저 이름"),
                "availability": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.FORMAT_BINARY),
                    description="하루를 48등분 (30분 단위) 한 Blob 형태, 이벤트에 추가된 날짜 순서대로 리스트로 전달",
                ),
            },
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        event_id: int = kwargs.get("pk")

        try:
            associated_dates: List[EventDate] = get_list_or_404(
                EventDate, event_id=event_id
            )
        except Http404:
            raise InstanceNotFound("event with provided id does not exist")

        name: str = request.data.get("name")
        availability: List[bytes] = request.data.get("availability")
        schedules: List[Schedule] = []

        for i in range(len(associated_dates)):
            data = {
                "name": name,
                "date_id": associated_dates[i].id,
                "event_id": event_id,
                "availability": availability[i],
            }
            serializer = self.get_serializer(data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            schedules.append(serializer.data)

        return Response(schedules, status=status.HTTP_201_CREATED)


class ScheduleDetail(generics.UpdateAPIView):
    """
    Updates a member's schedule associated with a certain date
    """

    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()
    allowed_methods = ["PATCH", "PUT"]

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.kwargs["name"]
        event_id = self.kwargs["pk"]
        qs = qs.filter(name=name, event_id=event_id)
        return qs

    def get_objects(self, **kwargs):
        print(kwargs)
        return Schedule.objects.filter(
            name=self.kwargs["name"], event_id=self.kwargs["pk"]
        )

    @swagger_auto_schema(
        operation_summary="Update a member's schedule [as a whole] associated with an event",
        operation_description="Be sure to include blob list containing all dates",
        responses={
            200: openapi.Response("Success", ScheduleSerializer),
            400: "Validation error",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "availability": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.FORMAT_BINARY),
                    description="하루를 48등분 (30분 단위) 한 Blob 형태, 이벤트에 추가된 날짜 순서대로 리스트로 전달",
                ),
            },
        ),
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        event_id = kwargs.get("pk")
        schedules = self.get_objects()
        availability: List[bytes] = request.data.get("availability")

        try:
            associated_dates: List[EventDate] = get_list_or_404(
                EventDate, event_id=event_id
            )
        except Http404:
            raise InstanceNotFound("event with provided id does not exist")

        if len(availability) != len(associated_dates):
            raise ValidationError(
                "availability list length does not match event-associated dates"
            )

        result: List[Schedule] = []

        for i in range(len(availability)):
            schedules[i].availability = availability[i]
            schedules[i].updated_at = datetime.now()
            serializer = self.get_serializer(schedules[i])
            if serializer.is_valid(raise_exception=True):
                serializer.save(updated_at=datetime.now())
            result.append(serializer.data)

            return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update a member's schedule by date associated with an event",
        responses={
            200: openapi.Response("Success", ScheduleSerializer),
            400: "Validation error",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "date": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="수정하고자 하는 날짜"
                ),
                "availability": openapi.Schema(
                    type=openapi.FORMAT_BINARY,
                    description="하루를 48등분 (30분 단위) 하여 Blob 형태로 전달",
                ),
            },
        ),
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass
