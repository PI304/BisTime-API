from typing import List
from urllib.parse import unquote

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, filters, pagination
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.team.models import Team, SubGroup
from apps.team.serializers import TeamMemberFixedScheduleSerializer
from apps.team.services import TeamMemberFixedScheduleService
from config.exceptions import InstanceNotFound


class TeamMemberFixedScheduleCreateView(generics.CreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamMemberFixedScheduleSerializer

    def post(self, request, *args, **kwargs):
        try:
            team = get_object_or_404(Team, uuid=request.data.get("team"))
        except Http404:
            raise InstanceNotFound("team does not exist for the provided uuid")

        serializer = self.get_serializer(data=request.data)

        data: dict = {}
        if serializer.is_valid(raise_exception=True):
            serializer.save(team_name=team.name)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamMemberFixedScheduleGetView(generics.ListAPIView):
    queryset = Team.objects.all()

    def get_team(self):
        return self.queryset.filter(uuid=self.kwargs.get("uuid")).first()

    def get(self, request, *args, **kwargs):
        subgroup = request.GET.get("subgroup")
        name = request.GET.get("name")

        team = self.get_team()

        if subgroup:
            try:
                get_object_or_404(SubGroup, name=subgroup)
            except Http404:
                raise InstanceNotFound("subgroup with provided name does not exist")

        if name:
            # Team 내, Subgroup 내 member name
            member_schedule = TeamMemberFixedScheduleService.get_member_schedule(
                team.name, name, subgroup
            )
            data = {
                "name": name,
                "subgroup": subgroup,
                "week_schedule": member_schedule,
            }
            return Response(data, status=status.HTTP_200_OK)
        elif subgroup and not name:
            # Subgroup 내 모든 fixed schedule
            return Response(
                TeamMemberFixedScheduleService.get_subgroup_schedules(
                    team.name, subgroup
                )
            )
        elif not subgroup and not name:
            # Team 내 모든 fixed schedule
            return Response(
                TeamMemberFixedScheduleService.get_all_member_schedules(team.name),
                status=status.HTTP_200_OK,
            )


class TeamMemberFixedScheduleDestroyView(generics.DestroyAPIView):
    # TODO: delete view -> request header parameter 사용 authorization header basic base64 인코딩
    pass
