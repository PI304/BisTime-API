from datetime import datetime
from pytz import timezone
from rest_framework.relations import PrimaryKeyRelatedField

from config.settings.base import TIME_ZONE

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.event.models import Event, EventDate, Schedule
from typing import Dict


class EventSerializer(serializers.ModelSerializer):
    # TODO: associated_team
    # associated_team = PrimaryKeyRelatedField(queryset=Team.objects.all())

    class Meta:
        model = Event
        fields = [
            "id",
            "uuid",
            "associated_team",
            "title",
            "start_time",
            "end_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "created_at",
            "updated_at",
        ]

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
    class Meta:
        model = EventDate
        fields = ["id", "event", "date", "created_at", "updated_at"]
        read_only_fields = [
            "id",
            "event" "created_at",
            "updated_at",
        ]

    def validate_date(self, value: datetime) -> datetime:
        """
        Check if date is of future value
        """
        if value >= datetime.now(timezone(TIME_ZONE)):
            raise ValidationError("should be a future date")

        return value


class ScheduleSerializer(serializers.ModelSerializer):
    event = PrimaryKeyRelatedField(queryset=Event.objects.all())
    date = PrimaryKeyRelatedField(queryset=EventDate.objects.all())

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
            "name",
            "event",
            "created_at",
            "updated_at",
        ]

    def validate_availability(self, value: bytes) -> bytes:
        if len(value) != 48:
            raise ValidationError("availability must be 48 length bytes")

        return value
