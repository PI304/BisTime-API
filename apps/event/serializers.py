import datetime

from apps.event.services import EventService
from config.custom_fields import TeamUUIDField
from config.mixins import TimeBlockMixin

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.event.models import Event, EventDate, Schedule
from typing import Dict, Union


class EventSerializer(serializers.ModelSerializer):
    associated_team = TeamUUIDField()
    availability = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "uuid",
            "associated_team",
            "title",
            "start_time",
            "end_time",
            "availability",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "availability",
            "associated_team",
            "created_at",
            "updated_at",
        ]

    def get_availability(self, obj):
        event_service: EventService = EventService(obj.id)
        availability: Union[dict[str, str], None] = event_service.get_availability_str()
        return availability

    def validate(self, data: Dict) -> Dict:
        """
        Validate model input
        """
        TimeBlockMixin.validate_time_data(data)

        return data


class EventDateSerializer(serializers.ModelSerializer):
    event = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EventDate
        fields = ["id", "event", "date", "created_at", "updated_at"]
        read_only_fields = [
            "id",
            "event",
            "created_at",
            "updated_at",
        ]

    def validate_date(self, value: datetime.date) -> datetime.date:
        """
        Check if date is of future value
        """
        print(type(value))
        if value <= datetime.date.today():
            raise ValidationError("should be a future date")

        return value


class ByteArrayField(serializers.Field):
    def to_representation(self, value: list[int]) -> str:
        return "".join(str(e) for e in value)

    def to_internal_value(self, data):
        if not isinstance(data, bytearray):
            msg = "Incorrect type. Expected a bytearray, but got %s"
            raise ValidationError(msg % type(data).__name__)
        if len(list(data)) != 48:
            raise ValidationError("length of availability array should be 48")
        return data


class ScheduleSerializer(serializers.ModelSerializer):
    date: str = serializers.StringRelatedField()
    availability = ByteArrayField()

    class Meta:
        model = Schedule
        fields = [
            "id",
            "name",
            "event",
            "date",
            "availability",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "date",
            "created_at",
            "updated_at",
        ]
