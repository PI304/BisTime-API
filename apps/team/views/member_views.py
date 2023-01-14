from typing import Any, Union

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.team.models import Team, TeamMember
from apps.team.serializers import TeamMemberSerializer, WeekScheduleSerializer
from apps.team.services import TeamMemberService
from config.exceptions import InstanceNotFound, DuplicateInstance


class TeamMemberCreateView(generics.CreateAPIView):
    serializer_class = TeamMemberSerializer
    allowed_methods = ["POST"]

    @swagger_auto_schema(
        operation_summary="Add a team member",
        responses={
            201: openapi.Response("Success", TeamMemberSerializer),
            400: "Validation error",
            404: "Not found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["team", "subgroup", "name", "weekSchedule"],
            properties={
                "team": openapi.Schema(
                    type=openapi.TYPE_STRING, description="멤버를 추가할 팀의 uuid"
                ),
                "subgroup": openapi.Schema(
                    type=openapi.TYPE_STRING, description="멤버를 추가할 팀의, 서브그룹의 이름"
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="추가할 멤버 이름"
                ),
                "weekSchedule": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="0 혹은 1 로 구성된 length 48 짜리 string",
                    ),
                    description="7개의 string 을 리스트로 전달",
                ),
            },
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        name = request.data.get("name")
        team = request.data.get("team")

        try:
            existing_member = get_object_or_404(TeamMember, name=name, team__uuid=team)
            raise DuplicateInstance("team member with the provided name already exists")
        except Http404:
            pass

        serializer = self.get_serializer(data=request.data)

        saved_member: Union[TeamMember, None] = None

        try:
            if serializer.is_valid(raise_exception=True):
                saved_member = serializer.save()

                data = serializer.data
                data["week_schedule"] = request.data.get("week_schedule")

                s_serializer = WeekScheduleSerializer(data=data)
                if s_serializer.is_valid(raise_exception=True):
                    s_serializer.save()
        except ValidationError as e:
            saved_member.delete()
            raise e

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TeamMemberListView(generics.ListAPIView, generics.DestroyAPIView):
    queryset = Team.objects.all()
    allowed_methods = ["GET", "DELETE"]
    paginator = None

    name_param = openapi.Parameter(
        "name", openapi.IN_QUERY, description="팀원 이름", type=openapi.TYPE_STRING
    )
    subgroup_param = openapi.Parameter(
        "subgroup",
        openapi.IN_QUERY,
        description="조회하고자 하는 서브그룹의 이름",
        type=openapi.TYPE_STRING,
    )

    def get_team(self):
        return self.queryset.filter(uuid=self.kwargs.get("uuid")).first()

    @swagger_auto_schema(
        operation_summary="Get schedules",
        operation_description="name 쿼리스트링을 통해 특정 멤버의 스케줄을 조회하거나 subgroup 쿼리스트링을 통해 팀 내 특정 서브그룹에 속해있는 모든 멤버들의 스케줄을 "
        "조회함. 쿼리스트링이 없으면 팀 전체 멤버의 스케줄 조회",
        responses={
            201: openapi.Response("Success", TeamMemberSerializer),
            400: "Validation error",
            404: "Not found",
        },
        manual_parameters=[name_param, subgroup_param],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        name = request.GET.get("name")
        subgroup = request.GET.get("subgroup")

        team = self.get_team()

        if name:
            try:
                member = get_object_or_404(TeamMember, name=name, team_id=team.id)
            except Http404:
                raise InstanceNotFound(
                    "team member with the provided name does not exist in the team"
                )

            # 개인 스케줄
            member_schedule = TeamMemberService.get_member_schedule(team.name, name)
            data = {
                "name": name,
                "subgroup": member.subgroup.name,
                "week_schedule": member_schedule,
            }
            return Response(data, status=status.HTTP_200_OK)
        elif subgroup:
            # Subgroup 내 모든 스케줄
            return Response(
                TeamMemberService.get_subgroup_schedules(team.name, subgroup)
            )
        elif not subgroup and not name:
            # Team 내 모든 fixed schedule
            return Response(
                TeamMemberService.get_all_member_schedules(team.name),
                status=status.HTTP_200_OK,
            )


@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        operation_summary="Update team member's subgroup",
        operation_description="스케줄 초기화시에도 해당 엔드포인트 사용 (모두 1로 초기화)",
        responses={
            200: openapi.Response("Success", TeamMemberSerializer),
            400: "Validation error",
            404: "Not found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "subgroup": openapi.Schema(
                    type=openapi.TYPE_STRING, description="바꿀 서브그룹의 이름"
                ),
                "weekSchedule": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING, description="길이 48, 1과 0으로 이루어진 문자열"
                    ),
                    description="새로운 스케줄",
                ),
            },
        ),
    ),
)
@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Delete a team member and its schedule",
        operation_description="스케줄 초기화하고 싶은 경우 patch method 이용",
        responses={
            200: openapi.Response("Success", TeamMemberSerializer),
            404: "Not found",
        },
    ),
)
class TeamMemberDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = TeamMember.objects.all()
    allowed_methods = ["PATCH", "DELETE"]
    serializer_class = TeamMemberSerializer

    def get_queryset(self):
        return self.queryset.filter(id=self.kwargs.get("pk"))

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data={"subgroup": request.data.get("subgroup")}, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_at=timezone.now())

        data = serializer.data
        if request.data.get("week_schedule"):
            data["week_schedule"] = self.request.data.get("week_schedule")

            s_serializer = WeekScheduleSerializer(data=data)
            if s_serializer.is_valid(raise_exception=True):
                s_serializer.save()

        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        self.perform_destroy(instance)
        TeamMemberService.delete_schedule(instance.team.name, name=kwargs.get("name"))
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)
