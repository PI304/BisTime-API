from __future__ import annotations

import datetime
from typing import Union

import shortuuid
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
import uuid

from rest_framework.request import Request

from apps.event.models import Event, Schedule, EventDate
from config.exceptions import InstanceNotFound


class EventService(object):
    def __init__(
        self: EventService, event_id: int, request: Union[Request, None] = None
    ):
        self.event = self.get_event_by_id(event_id)
        self.request = request

    @staticmethod
    def get_event_by_id(event_id: int) -> Event:
        try:
            event: Event = get_object_or_404(Event, id=event_id)
        except Http404:
            raise InstanceNotFound("event with the provided id does not exist")
        return event

    @staticmethod
    def generate_uuid() -> str:
        u = uuid.uuid4()
        s = shortuuid.encode(u)
        return s

    def calculate_event_availability(self) -> dict[str, list[int]]:
        associated_dates = EventDateService.get_dates_by_event_id(self.event.id)

        availability_obj = {}

        for date in associated_dates:
            availabilities = [0] * 48
            schedules = get_list_or_404(
                Schedule, event_id=self.event.id, date_id=date.id
            )
            for s in schedules:
                availabilities = [
                    x + y for x, y in zip(availabilities, list(s.availability))
                ]
            availability_obj[str(date.date)] = availabilities

        return availability_obj

    def get_availability_str(self) -> dict[str, str]:
        availability_obj: dict[
            str, Union[str, list[int]]
        ] = self.calculate_event_availability()
        for (k, v) in availability_obj.items():
            availability_obj[k] = "".join(str(e) for e in v)

        return availability_obj


class EventDateService(object):
    def __init__(self: EventDateService, request: Request, view=None):
        self.request = request
        self.view = view

    def get_serialized_event_dates(self):
        queryset = self.view.filter_queryset(self.view.get_queryset())

        page = self.view.paginate_queryset(queryset)
        if page is not None:
            serializer = self.view.get_serializer(page, many=True)
            return self.view.get_paginated_response(serializer.data)

        serializer = self.view.get_serializer(queryset, many=True)
        return serializer

    @staticmethod
    def get_dates_by_event_id(event_id: int):
        try:
            dates: list[EventDate] = get_list_or_404(EventDate, event_id=event_id)
        except Http404:
            raise InstanceNotFound("dates with the provided event id does not exist")
        return dates


class ScheduleService(object):
    def __init__(
        self: ScheduleService, request: Request, schedule_id: Union[int, None] = None
    ):
        self.schedule = self.get_schedule_by_id(schedule_id)
        self.request = request

    @staticmethod
    def get_schedule_by_id(schedule_id: int):
        try:
            schedule: Schedule = get_object_or_404(Schedule, id=schedule_id)
        except Http404:
            raise InstanceNotFound("schedule with the provided id does not exist")
        return schedule

    @staticmethod
    def get_schedules_by_event_id(event_id: int):
        try:
            schedules: list[Schedule] = get_list_or_404(Schedule, event_id=event_id)
        except Http404:
            raise InstanceNotFound(
                "schedules with the provided event id does not exist"
            )
        return schedules
