from django.http import Http404
from django.shortcuts import get_list_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.event.serializers import EventSerializer
from apps.team.models import Team, TeamRegularEvent, SubGroup


class TeamSerializer(serializers.ModelSerializer):
    security_question = serializers.CharField(
        source="get_security_question_display", read_only=True
    )
    subgroups = serializers.SerializerMethodField()
    # security_question = (
    #     serializers.StringRelatedField()
    # )  # TODO: security question models

    class Meta:
        model = Team
        fields = [
            "id",
            "uuid",
            "name",
            "subgroups",
            "admin_code",
            "security_question",
            "custom_security_question",
            "security_answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "admin_code",
            "subgroups",
            "custom_security_question",
            "created_at",
            "updated_at",
        ]

    def get_subgroups(self, obj) -> list[str]:
        subgroups: list[str] = []
        try:
            subgroup_instances: list[SubGroup] = get_list_or_404(
                SubGroup, team_id=obj.id
            )
        except Http404:
            return subgroups

        return [s.name for s in subgroup_instances]


class TeamRegularEventSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = TeamRegularEvent
        fields = [
            "id",
            "uuid",
            "team",
            "title",
            "description",
            "day",
            "start_time",
            "end_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    def validate(self, data: dict) -> dict:
        """
        Validate model input
        """
        if "start_time" in data:
            EventSerializer.time_validation(data["start_time"])

        if "end_time" in data:
            EventSerializer.time_validation(data["end_time"])

        if "start_time" in data and "end_time" in data:
            if (
                int(data["end_time"].split(":")[0])
                - int(data["start_time"].split(":")[0])
                < 0
            ):
                raise ValidationError("end_time should be larger than start_time")
        if data["day"] < 0 or data["day"] > 6:
            raise ValidationError("day should be between 0 and 6")

        return data


class SubgroupSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = SubGroup
        fields = ["id", "team", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "team", "created_at", "updated_at"]
