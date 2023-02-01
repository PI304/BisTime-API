from typing import List, Dict

from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.event.serializers import EventSerializer
from apps.team.models import Team, TeamRegularEvent, SubGroup, TeamMember
from apps.team.services import TeamMemberService
from config.custom_fields import TeamSubgroupField
from config.exceptions import InstanceNotFound, DuplicateInstance
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
        subgroups = obj.subgroups.all()
        return [s.name for s in subgroups]

    def validate(self, data: Dict) -> Dict:
        TimeBlockMixin.validate_time_data(
            data.get("start_time", None), data.get("end_time", None)
        )

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
        TimeBlockMixin.validate_time_data(
            data.get("start_time", None), data.get("end_time", None)
        )
        if "day" in data and (data["day"] < 0 or data["day"] > 6):
            raise ValidationError("day should be between 0 and 6")

        return data


class SubgroupSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = SubGroup
        fields = ["id", "team", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "team", "created_at", "updated_at"]


class TeamMemberSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField(read_only=True)
    subgroup = TeamSubgroupField()

    class Meta:
        model = TeamMember
        fields = ["id", "name", "team", "subgroup", "created_at", "updated_at"]
        read_only_fields = ["id", "subgroup", "team", "created_at", "updated_at"]

    def get_team(self, obj):
        return obj.name

    def create(self, validated_data):
        try:
            existing_member = get_object_or_404(TeamMember, name=validated_data["name"])
            raise DuplicateInstance("member with the provided name already exists.")
        except Http404:
            return TeamMember.objects.create(
                team_id=validated_data["team"].id,
                subgroup_id=validated_data["subgroup"],
                name=validated_data["name"],
            )

    def update(self, instance, validated_data):
        if "subgroup" in validated_data:
            instance.subgroup_id = validated_data["subgroup"]
        instance.updated_at = timezone.now()
        instance.save(update_fields=["subgroup", "updated_at"])
        return instance


class WeekScheduleSerializer(serializers.Serializer):
    team = serializers.SerializerMethodField(read_only=True)
    subgroup = TeamSubgroupField()
    name = serializers.CharField(max_length=20)
    week_schedule = serializers.ListField(min_length=7, max_length=7)

    def get_team(self, obj):
        return obj.name

    def validate_week_schedule(self, value):
        for s in value:
            if not isinstance(s, str):
                raise ValidationError("list items should be of string type")
            if len(s) != 48:
                raise ValidationError("each items should be 48-length long")
        return value

    def validate_team(self, value):
        try:
            team = get_object_or_404(Team, id=value.id)
        except Http404:
            raise InstanceNotFound("team with the provided uuid does not exist")

        return value

    def save(self):
        schedule_bytes: List[bytearray] = []

        try:
            team = get_object_or_404(Team, id=self.validated_data["team"].id)
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
