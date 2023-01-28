import pytest

from apps.event.models import Event, EventDate, Schedule
from apps.event.services import EventService


class TestEventService(object):
    def test_get_event_by_id(self, create_event):
        result_id = 999
        event = EventService.get_event_by_id(result_id)
        assert event.id == result_id

    def test_get_event_by_uuid(self, create_event):
        result_uuid = "dbWUg9io46UXYNsiJrPhfR"
        event = EventService.get_event_by_uuid(result_uuid)
        assert event.uuid == result_uuid

    def test_generate_uuid(self):
        assert len(EventService.generate_uuid()) == 22

    def test_get_availability_str(
        self, create_event, create_event_dates, create_schedule
    ):
        # 2023-02-21 는 두 명 중 한명 만 되므로 '1' * 48
        result = {"2023-02-21": "1" * 48, "2023-02-22": "0" * 48}
        event_id = 999
        event_service = EventService(event_id)
        assert result == event_service.get_availability_str()
