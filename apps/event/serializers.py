import datetime

from apps.event.services import EventService
from config.mixins import TimeBlockMixin

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.event.models import Event, EventDate, Schedule
from typing import Dict, Union


class EventSerializer(serializers.ModelSerializer):
    associated_team = serializers.SerializerMethodField(read_only=True)
    availability = serializers.SerializerMethodField(read_only=True)

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
        availability: Union[dict[str, str], None] = EventService.get_availability_str(
            obj
        )
        return availability

    def get_associated_team(self, obj):
        if obj.associated_team is None:
            return None
        return obj.associated_team.name

    def validate(self, data: Dict) -> Dict:
        """
        Validate model input
        """
        TimeBlockMixin.validate_time_data(data)

        return data


class EventDateSerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EventDate
        fields = ["id", "event", "date", "created_at", "updated_at"]
        read_only_fields = [
            "id",
            "event",
            "created_at",
            "updated_at",
        ]

    def get_event(self, obj):
        return obj.event.uuid

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
    date: str = serializers.SerializerMethodField(read_only=True)
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
            "event",
            "created_at",
            "updated_at",
        ]

    def get_date(self, obj):
        return str(obj.date.date)
