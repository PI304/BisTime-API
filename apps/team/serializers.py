from typing import List, Dict

from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.event.serializers import EventSerializer
from apps.team.models import Team, TeamRegularEvent, SubGroup, TeamMember
from apps.team.services import TeamMemberService
from config.exceptions import InstanceNotFound
from config.mixins import TimeBlockMixin


class TeamSerializer(serializers.ModelSerializer):
    security_question = serializers.CharField(
        source="get_security_question_display", read_only=True
    )
    subgroups = serializers.SerializerMethodField()

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
            "start_time",
            "end_time",
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

    def validate(self, data: Dict) -> Dict:
        print(data)
        TimeBlockMixin.validate_time_data(data)

        # TODO: validate security question index number
        return data


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


class TeamUUIDField(serializers.Field):
    def to_representation(self, value: Team) -> str:
        team = get_object_or_404(Team, id=value.id)
        return team.uuid

    def to_internal_value(self, data):
        print(data)
        if not isinstance(data, str):
            msg = "Incorrect type. Expected a str (uuid), but got %s"
            raise ValidationError(msg % type(data).__name__)
        try:
            team = get_object_or_404(Team, uuid=data)
        except Http404:
            raise InstanceNotFound("team with the provided uuid does not exist")
        return team.id


class TeamSubgroupField(serializers.Field):
    def to_representation(self, value: SubGroup) -> str:
        subgroup = get_object_or_404(SubGroup, id=value.id)
        return subgroup.name

    def to_internal_value(self, data):
        if not isinstance(data, str):
            msg = "Incorrect type. Expected a str (name), but got %s"
            raise ValidationError(msg % type(data).__name__)
        try:
            subgroup = get_object_or_404(SubGroup, name=data)
        except Http404:
            raise InstanceNotFound("subgroup with the provided id does not exist")
        return subgroup.id


class TeamMemberSerializer(serializers.ModelSerializer):
    team = TeamUUIDField()
    subgroup = TeamSubgroupField()

    class Meta:
        model = TeamMember
        fields = ["id", "name", "team", "subgroup", "created_at", "updated_at"]
        read_only_fields = ["id", "subgroup", "team", "created_at", "updated_at"]

    def create(self, validated_data):
        print(validated_data)
        return TeamMember.objects.create(
            team_id=validated_data["team"],
            subgroup_id=validated_data["subgroup"],
            name=validated_data["name"],
        )

    def update(self, instance, validated_data):
        instance.subgroup_id = validated_data["subgroup"]
        instance.updated_at = validated_data["updated_at"]
        instance.save(update_fields=["subgroup", "updated_at"])
        return instance


class WeekScheduleSerializer(serializers.Serializer):
    team = TeamUUIDField()
    # TODO: add subgroup
    name = serializers.CharField(max_length=20)
    week_schedule = serializers.ListField(min_length=7, max_length=7)

    def validate_week_schedule(self, value):
        for s in value:
            if not isinstance(s, str):
                raise ValidationError("list items should be of string type")
            if len(s) != 48:
                raise ValidationError("each items should be 48-length long")
        return value

    def validate_team(self, value):
        try:
            team = get_object_or_404(Team, id=value)
        except Http404:
            raise InstanceNotFound("team with the provided uuid does not exist")

        return value

    def save(self):
        schedule_bytes: List[bytearray] = []

        try:
            team = get_object_or_404(Team, id=self.validated_data["team"])
        except Http404:
            raise InstanceNotFound("team with the provided uuid does not exist")

        for bytes_string in self.validated_data["week_schedule"]:
            schedule_bytes.append(bytearray([int(x) for x in bytes_string]))

        bitmap_bytes: bytes = TeamMemberService.create_schedule_bitmap_bytes(
            schedule_bytes
        )
        TeamMemberService.save_schedule(
            bitmap_bytes,
            team.name,
            self.validated_data["name"],
        )
