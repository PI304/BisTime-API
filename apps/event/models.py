from django.db import models
from django.core.validators import MinLengthValidator
from apps.team.models import Team
from config.mixins import TimeStampMixin, TimeBlockMixin


class Event(TimeStampMixin, TimeBlockMixin):
    """
    A single event with date and time range
    """

    id = models.BigAutoField(primary_key=True)
    uuid = models.CharField(
        max_length=22, validators=[MinLengthValidator(22)], null=False
    )
    associated_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, null=True, related_name="event"
    )
    title = models.CharField(max_length=100, null=False)

    class Meta:
        db_table = "event"

    def __str__(self) -> str:
        return f"[{self.id}] {self.title}"

    def __repr__(self) -> str:
        return f"Event({self.id}, {self.title})"


class EventDate(TimeStampMixin):
    """
    Associated dates of an event
    """

    id = models.BigAutoField(primary_key=True)
    event = models.ForeignKey(
        Event, null=False, on_delete=models.CASCADE, related_name="event_date"
    )
    date = models.DateField(null=False)

    class Meta:
        db_table = "event_date"

    def __str__(self) -> str:
        return f"[{self.id}] ({self.event}, {self.date})"

    def __repr__(self) -> str:
        return f"EventDate({self.id}, {self.event}, {self.date})"


class Schedule(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    event = models.ForeignKey(
        Event, null=False, on_delete=models.CASCADE, related_name="schedule"
    )
    date = models.ForeignKey(EventDate, null=False, on_delete=models.DO_NOTHING)
    availability = models.BinaryField(null=True, default=bytes(48))

    class Meta:
        db_table = "schedule"

    def __str__(self) -> str:
        return f"[{self.id}] {self.name}"

    def __repr__(self) -> str:
        return f"Schedule({self.id}, {self.name})"
