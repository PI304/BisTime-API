from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.team.models import Team, SubGroup
from config.exceptions import InstanceNotFound


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
        return team


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
            raise InstanceNotFound("subgroup with the provided name does not exist")
        return subgroup.id
