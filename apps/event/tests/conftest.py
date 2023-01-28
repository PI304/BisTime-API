import pytest

from apps.event.models import Event, EventDate, Schedule


@pytest.fixture(autouse=False, scope="function")
def create_event(db):
    Event.objects.create(
        id=999,
        uuid="dbWUg9io46UXYNsiJrPhfR",
        title="test event 1",
        start_time="09:00",
        end_time="21:00",
    )
    Event.objects.create(
        id=998,
        uuid="89PKcffHuwBA9uCnGWraNZ",
        title="test event 2",
        start_time="10:00",
        end_time="21:00",
    )


@pytest.fixture(autouse=False, scope="function")
def create_event_dates(db):
    EventDate.objects.create(id=999, event_id=999, date="2023-02-21")
    EventDate.objects.create(id=998, event_id=999, date="2023-02-22")


@pytest.fixture(autouse=False, scope="function")
def create_schedule(db):
    Schedule.objects.create(
        id=999, name="지구", event_id=999, date_id=999, availability=bytearray([0] * 48)
    )
    Schedule.objects.create(
        id=998, name="지구2", event_id=999, date_id=999, availability=bytearray([1] * 48)
    )
