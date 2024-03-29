import pytest

from apps.event.models import Event, EventDate, Schedule
from apps.event.serializers import ScheduleSerializer
from apps.event.services import EventService

from django.test.utils import CaptureQueriesContext


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
        from django.db import connection, close_old_connections

        with CaptureQueriesContext(connection) as (expected_num_queries):
            # 2023-02-21 는 두 명 중 한명 만 되므로 '1' * 48
            result = {
                "2023-02-21": "1" * 48,
                "2023-02-22": "0" * 48,
                "2023-02-23": "1" * 48,
            }

            event = (
                Event.objects.select_related("associated_team")
                .prefetch_related("event_date", "schedule")
                .get(id=999)
            )

            assert result == EventService.get_availability_str(event)
            assert len(expected_num_queries.captured_queries) <= 4

            close_old_connections()

    def test_get_related_dates(self, create_event, create_event_dates):
        from django.db import connection, close_old_connections

        with CaptureQueriesContext(connection) as (expected_num_queries):
            queryset = EventDate.objects.select_related("event").filter(
                event__uuid="dbWUg9io46UXYNsiJrPhfR"
            )
            l = list(queryset)
            assert len(expected_num_queries.captured_queries) == 1

            close_old_connections()

    def test_get_related_schedule_for_event(
        self, create_event, create_event_dates, create_schedule
    ):
        from django.db import connection, close_old_connections

        with CaptureQueriesContext(connection) as (expected_num_queries):
            queryset = (
                Schedule.objects.select_related("event", "date")
                .filter(event__uuid="dbWUg9io46UXYNsiJrPhfR")
                .order_by("date__date")
            )
            serializer = ScheduleSerializer(queryset, many=True)
            s = serializer.data
            print(expected_num_queries.captured_queries)
            assert len(expected_num_queries.captured_queries) == 1

            close_old_connections()
