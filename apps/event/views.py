from datetime import datetime, date
from typing import Any, List
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.request import Request

from apps.event.models import Event, EventDate, Schedule
from apps.event.serializers import (
    EventSerializer,
    EventDateSerializer,
    ScheduleSerializer,
)
from apps.event.services import EventService, EventDateService
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
    queryset = Event.objects.all().order_by("id")

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


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Delete an event",
        operation_description="[Warning] Cascading deletion for all related dates and schedules",
        responses={200: openapi.Response("Success", EventDateSerializer)},
    ),
)
class EventDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    allowed_methods = ["PATCH", "DELETE"]

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
    queryset = EventDate.objects.all().order_by("date")
    allowed_methods = ["POST"]

    def get_queryset(self):
        qs = self.queryset.filter(event=self.kwargs.get("pk"))
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

        service = EventDateService(request, self)
        serialized_dates = service.get_serialized_event_dates()

        return Response(serialized_dates.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Delete a date associated with an event",
        operation_description="[Warning] Cascading deletion for associated schedules",
        responses={200: openapi.Response("Success", EventDateSerializer)},
    ),
)
class EventDateDestroyView(generics.DestroyAPIView):
    serializer_class = EventDateSerializer
    queryset = EventDate.objects.all()
    allowed_methods = ["DELETE"]


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Get all schedule data associated with a single instant event",
        responses={200: openapi.Response("Success", ScheduleSerializer)},
    ),
)
class ScheduleView(generics.ListAPIView):
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all().order_by("date__date")
    allowed_methods = ["GET"]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        qs = self.queryset.filter(event=self.kwargs.get("pk"))
        return qs


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Get user's schedule data associated with a single instant event",
        responses={200: openapi.Response("Success", ScheduleSerializer)},
    ),
)
class UserScheduleView(
    generics.ListAPIView, generics.UpdateAPIView, generics.DestroyAPIView
):
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all().order_by("date__date")
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    allowed_methods = ["GET", "PATCH", "DELETE"]

    def get_queryset(self):
        qs = self.queryset.filter(
            event=self.kwargs.get("pk"), name=self.kwargs.get("name")
        )
        return qs

    def get_objects(self) -> List[Schedule]:
        return Schedule.objects.filter(
            event=self.kwargs.get("pk"), name=self.kwargs.get("name")
        )

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
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.FORMAT_BINARY, description="0 혹은 1"
                    ),
                    description="하루를 48등분 (30분 단위) 하여 byte array 형태로 전달",
                ),
            },
        ),
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_queryset().filter(date=kwargs.get("date")).first()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_at=datetime.now())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Destroys all schedules associated with a name",
        responses={204: "No content"},
    )
    def delete(self, request: Request, *args: Any, **kwargs) -> Response:
        schedules: List[Schedule] = self.get_objects()
        for s in schedules:
            s.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BulkCreateUserScheduleView(generics.CreateAPIView):
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()
    allowed_methods = ["POST"]

    @swagger_auto_schema(
        operation_summary="Add user's schedule to an event for all dates",
        operation_description="overrides existing schedules",
        responses={201: openapi.Response("Success", ScheduleSerializer)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "availability"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="유저 이름"),
                "availability": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.FORMAT_BINARY, description="0 혹은 1"
                        ),
                        description="0 혹은 1 로 구성된 length 48 짜리 byte array",
                    ),
                    description="이벤트에 추가된 날짜 순서대로 byte array 전달",
                ),
            },
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        event_id: int = kwargs.get("pk")
        name: str = request.data.get("name")

        try:
            associated_dates: List[EventDate] = get_list_or_404(
                EventDate, event_id=event_id, name=name
            )
        except Http404:
            raise InstanceNotFound("event with provided id does not exist")

        availability: List[List[bytes]] = request.data.get("availability")

        if len(associated_dates) != len(availability):
            raise ValidationError(
                "length of availability does not match associated dates"
            )

        schedules: List[Schedule] = []

        for i in range(len(associated_dates)):
            try:
                instance = get_object_or_404(
                    Schedule, name=name, date=associated_dates[i].id
                )

                # instance 있을 때 -> update Instance
                serializer = self.get_serializer(
                    instance, data={"availability": availability[i]}, partial=True
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save(updated_at=datetime.now())
                schedules.append(serializer.data)
            except Http404 as e:
                # instance 없을 때 -> 새로 생성
                data = {
                    "event": event_id,
                    "name": name,
                    "availability": availability[i],
                    "date": associated_dates[i].id,
                }
                serializer = self.get_serializer(data=data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                schedules.append(serializer.data)

        return Response(schedules, status=status.HTTP_201_CREATED)
