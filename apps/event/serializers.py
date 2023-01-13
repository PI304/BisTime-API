from datetime import datetime

from django.utils import timezone

from apps.event.services import EventService

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.event.models import Event, EventDate, Schedule
from typing import Dict, Union


class EventSerializer(serializers.ModelSerializer):
    # TODO: associated_team
    # associated_team = PrimaryKeyRelatedField(queryset=Team.objects.all())
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
            "associated_team",
            "availability",
            "created_at",
            "updated_at",
        ]

    def get_availability(self, obj):
        event_service: EventService = EventService(obj.id)
        availability: Union[dict[str, str], None] = event_service.get_availability_str()
        return availability

    @staticmethod
    def time_validation(time_exp: str):
        if ":" not in time_exp or len(time_exp) != 5 or len(time_exp.split(":")) != 2:
            raise ValidationError("_time should be of 'HH:MM' format")

        time_split = time_exp.split(":")

        if len(time_split[0]) != 2 or len(time_split[1]) != 2:
            raise ValidationError("_time should be of 'HH:MM' format")

        if int(time_split[0]) < 0 or int(time_split[0]) > 24:
            raise ValidationError("hours should be between 00 ~ 24")

        if not (time_split[1] == "30" or time_split[1] == "00"):
            raise ValidationError("minutes should be 00 or 30")

    def validate(self, data: Dict) -> Dict:
        """
        Validate model input
        """
        if "start_time" in data:
            self.time_validation(data["start_time"])

        if "end_time" in data:
            self.time_validation(data["end_time"])

        if "start_time" in data and "end_time" in data:
            if (
                int(data["end_time"].split(":")[0])
                - int(data["start_time"].split(":")[0])
                < 0
            ):
                raise ValidationError("end_time should be larger than start_time")

        # TODO: Check if team exists

        return data


class EventDateSerializer(serializers.ModelSerializer):
    # event = EventSerializer(read_only=True)

    class Meta:
        model = EventDate
        fields = ["id", "event", "date", "created_at", "updated_at"]
        read_only_fields = [
            "id",
            "event",
            "created_at",
            "updated_at",
        ]

    def validate_date(self, value: datetime) -> datetime:
        """
        Check if date is of future value
        """
        if value <= timezone.now():
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
    date = serializers.StringRelatedField()
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
