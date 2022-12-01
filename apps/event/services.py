from __future__ import annotations

import shortuuid
from django.shortcuts import get_object_or_404
import uuid

from rest_framework.request import Request

from apps.event.models import Event


class EventService(object):
    def __init__(self: EventService, request: Request):
        self.event = request.data

    def get_event_by_id(self: EventService):
        event = get_object_or_404(Event, id=self.event["id"])
        return event

    @staticmethod
    def generate_uuid() -> str:
        u = uuid.uuid4()
        s = shortuuid.encode(u)
        return s
