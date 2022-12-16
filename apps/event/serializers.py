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

    def validate(self, data: Dict) -> Dict:
        """
        Validate model input
        """

        if (
            (":" not in data["start_time"])
            or (":" not in data["end_time"])
            or len(data["start_time"].split(":")) != 2
            or len(data["end_time"].split(":")) != 2
        ):
            raise ValidationError("_time should be of 'HH:MM' format")

        start_time_list = data["start_time"].split(":")
        end_time_list = data["end_time"].split(":")

        if (
            len(start_time_list[0]) != 2
            or len(start_time_list[1]) != 2
            or len(end_time_list[0]) != 2
            or len(end_time_list[1]) != 2
        ):
            raise ValidationError("_time should be of 'HH:MM' format")

        if (
            int(start_time_list[0]) < 0
            or int(start_time_list[0]) > 24
            or int(end_time_list[0]) < 0
            or int(end_time_list[0]) > 24
        ):
            raise ValidationError("hours should be between 00 ~ 24")

        if not (start_time_list[1] == "30" or start_time_list[1] == "00") and (
            end_time_list[1] == "30" or end_time_list[1] == "00"
        ):
            raise ValidationError("minutes should be 00 or 30")

        if int(end_time_list[0]) - int(end_time_list[0]) > 0:
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
