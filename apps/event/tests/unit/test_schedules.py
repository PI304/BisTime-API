import pytest

from apps.event.models import Schedule
from apps.event.serializers import ScheduleSerializer


@pytest.mark.django_db
class TestSchedule(object):
    def setup_class(cls):
        cls.serializer = ScheduleSerializer

    def test_byte_array_field(self, create_event, create_event_dates, create_schedule):
        instance = Schedule.objects.get(id=999)
        serializer = self.serializer(instance=instance)
        result = serializer.data

        assert type(result["availability"]) == str
