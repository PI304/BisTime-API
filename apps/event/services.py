from __future__ import annotations

import datetime
from itertools import groupby
from operator import itemgetter
from typing import Union, Optional, Dict, List

import shortuuid
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
import uuid

from rest_framework.request import Request

from apps.event.models import Event, Schedule, EventDate
from config.exceptions import InstanceNotFound


class EventService:
    @staticmethod
    def get_event_by_id(event_id: int) -> Event:
        try:
            event: Event = get_object_or_404(Event, id=event_id)
        except Http404:
            raise InstanceNotFound("event with the provided id does not exist")
        return event

    @staticmethod
    def get_event_by_uuid(event_uuid: str) -> Event:
        try:
            event: Event = get_object_or_404(Event, uuid=event_uuid)
        except Http404:
            raise InstanceNotFound("event with the provided id does not exist")
        return event

    @staticmethod
    def generate_uuid() -> str:
        u = uuid.uuid4()
        s = shortuuid.encode(u)
        return s

    @staticmethod
    def __calculate_event_availability(
        event: Event,
    ) -> Union[dict[str, list[int]], None]:
        associated_dates: List[EventDate] = event.event_date.all()

        if len(associated_dates) == 0:
            return None

        schedules: List[dict] = event.schedule.values()

        # sort INFO data by 'company' key.
        schedules = sorted(schedules, key=itemgetter("date_id"))

        grouped_schedules: Dict[int, List[dict]] = {}

        for key, value in groupby(schedules, key=itemgetter("date_id")):
            grouped_schedules[key] = list(value)

        print(grouped_schedules)
        availability_obj = {}

        for date in associated_dates:
            availability_list = [0] * 48

            if date.id in grouped_schedules:
                associated_schedules: List[dict] = grouped_schedules.get(date.id, None)
                for s in associated_schedules:
                    availability_list = [
                        x + y
                        for x, y in zip(availability_list, list(s["availability"]))
                    ]
            else:
                pass

            availability_obj[str(date.date)] = availability_list

        return availability_obj

    @staticmethod
    def get_availability_str(event: Event) -> Dict[str, Union[str, List[int]]]:

        availability_obj: Optional[
            Dict[str, Union[str, List[int]]]
        ] = EventService.__calculate_event_availability(event)

        if availability_obj is None:
            return None
        else:
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
        return EventDate.objects.filter(event_id=event_id).all()


class ScheduleService(object):
    @staticmethod
    def get_schedule(event_id: int, date_id: int, name: str):
        return Schedule.objects.filter(
            event_id=event_id, date_id=date_id, name=name
        ).all()

    @staticmethod
    def get_schedules_by_event_id(event_id: int):
        try:
            schedules: list[Schedule] = get_list_or_404(Schedule, event_id=event_id)
        except Http404:
            raise InstanceNotFound(
                "schedules with the provided event id does not exist"
            )
        return schedules
