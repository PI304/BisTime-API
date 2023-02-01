from typing import Any

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.team.models import Team, TeamRegularEvent, SubGroup
from apps.team.serializers import (
    TeamSerializer,
    TeamRegularEventSerializer,
    SubgroupSerializer,
)
from apps.team.services import TeamService, TeamRegularEventService, TeamMemberService
from config.exceptions import InstanceNotFound

team_name_param = openapi.Parameter(
    "name", openapi.IN_QUERY, description="팀 이름", type=openapi.TYPE_STRING
)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_description="use query string 'name' to get a team by its name",
        manual_parameters=[team_name_param],
        responses={
            200: openapi.Response("Success", TeamSerializer),
            404: "Not found",
        },
    ),
)
class TeamView(generics.ListCreateAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    allowed_methods = ["GET", "POST"]
    pagination_class = None

    def get(self, request, *args, **kwargs):
        print(request.GET.get("name"))
        queryset = (
            self.get_queryset()
            .prefetch_related("subgroups")
            .filter(name=request.GET.get("name"))
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data[0])

    @swagger_auto_schema(
        operation_summary="Create Team",
        operation_description="Should expose admin code to user",
        responses={
            201: openapi.Response("Success", TeamSerializer),
            400: "Validation error",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "securityAnswer", "startTime", "endTime"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="팀 이름"),
                "securityQuestion": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="보안질문 엔트리 ID"
                ),
                "customSecurityQuestion": openapi.Schema(
                    type=openapi.TYPE_STRING, description="보안 질문 중 '기타' 선택한 경우"
                ),
                "securityAnswer": openapi.Schema(
                    type=openapi.TYPE_STRING, description="보안 질문 정답"
                ),
                "startTime": openapi.Schema(
                    type=openapi.TYPE_STRING, description="팀의 워크아워 시작 시간"
                ),
                "endTime": openapi.Schema(
                    type=openapi.TYPE_STRING, description="팀의 워크아워 종료 시간"
                ),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        serializer: TeamSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(
                admin_code=TeamService.generate_admin_code(),
                uuid=TeamService.generate_team_uuid(),
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Retrieve a team",
        operation_description="Get team data",
        responses={
            200: openapi.Response("Success", TeamSerializer),
            404: "Not found",
        },
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        operation_summary="Update team name",
        operation_description="Change team name",
        responses={
            200: openapi.Response("Success", TeamSerializer),
            400: "Validation error",
            404: "Not found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="새로운 팀 이름"
                ),
            },
        ),
    ),
)
@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Delete team",
        operation_description="[Warning] Every data related to this team will be deleted. Admin code needed",
        responses={204: "No content", 400: "Validation error", 404: "Not found"},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="새로운 팀 이름"
                ),
            },
        ),
    ),
)
class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    allowed_methods = ["PATCH", "GET", "DELETE"]
    lookup_field = "uuid"

    def get_queryset(self):
        return self.queryset.prefetch_related("subgroups").filter(
            uuid=self.kwargs.get("uuid")
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_at=timezone.now())

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        TeamMemberService.delete_schedule(instance.name)
        instance.delete()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["team-regular-events"],
        operation_summary="Get all regular events of a team",
        responses={
            200: openapi.Response("Success", TeamSerializer),
            404: "Not found",
        },
    ),
)
class TeamRegularEventListView(generics.ListCreateAPIView):
    serializer_class = TeamRegularEventSerializer
    queryset = TeamRegularEvent.objects.all()
    allowed_methods = ["GET", "POST"]

    def get_queryset(self):
        queryset = self.queryset.filter(team__uuid=self.kwargs.get("uuid"))
        return queryset

    def get_object(self) -> Team:
        # Get Team instance
        try:
            instance = get_object_or_404(Team, uuid=self.kwargs.get("uuid"))
        except Http404:
            raise InstanceNotFound("Team with the provided uuid doesn't exist")
        return instance

    @swagger_auto_schema(
        tags=["team-regular-events"],
        operation_summary="Create regular event for a team",
        responses={
            201: openapi.Response("Success", TeamRegularEventSerializer),
            400: "Validation error",
            404: "Not found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "day", "start_time", "end_time"],
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="정기 일정 제목"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="정기 일정 설명"
                ),
                "day": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="요일 인덱스, 월요일부터 시작하여 0부터 6까지"
                ),
                "startTime": openapi.Schema(
                    type=openapi.TYPE_STRING, description="HH:MM 형태"
                ),
                "endTime": openapi.Schema(
                    type=openapi.TYPE_STRING, description="HH:MM 형태"
                ),
            },
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        data: dict = request.data
        associated_team: Team = self.get_object()
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(
                uuid=TeamRegularEventService.generate_r_event_uuid(),
                team_id=associated_team.id,
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["team-regular-events"],
        operation_summary="Retrieve a regular event of a team",
        responses={
            200: openapi.Response("Success", TeamSerializer),
            404: "Not found",
        },
    ),
)
@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["team-regular-events"],
        operation_summary="Delete a regular event of a team",
        responses={
            204: "No content",
            404: "Not found",
        },
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["team-regular-events"],
        operation_summary="Update regular event for a team",
        responses={
            200: openapi.Response("Success", TeamRegularEventSerializer),
            400: "Validation error",
            404: "Not found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="정기 일정 제목"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="정기 일정 설명"
                ),
                "day": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="요일 인덱스, 월요일부터 시작하여 0부터 6까지"
                ),
                "startTime": openapi.Schema(
                    type=openapi.TYPE_STRING, description="HH:MM 형태"
                ),
                "endTime": openapi.Schema(
                    type=openapi.TYPE_STRING, description="HH:MM 형태"
                ),
            },
        ),
    ),
)
class TeamRegularEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamRegularEventSerializer
    queryset = TeamRegularEvent.objects.all()
    allowed_methods = ["GET", "PATCH", "DELETE"]

    def get_object(self) -> TeamRegularEvent:
        regular_event = self.queryset.filter(uuid=self.kwargs.get("uuid")).first()
        if not regular_event:
            raise InstanceNotFound(
                "regular event with the provided uuid does not exist"
            )
        return regular_event

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["team-subgroups"],
        operation_summary="Get all subgroups of a team",
        responses={
            200: openapi.Response("Success", SubgroupSerializer),
            404: "Not found",
        },
    ),
)
class SubgroupListView(generics.ListCreateAPIView):
    serializer_class = SubgroupSerializer
    queryset = SubGroup.objects.all()
    allowed_methods = ["POST", "GET"]

    def get_queryset(self):
        queryset = self.queryset.filter(team__uuid=self.kwargs.get("uuid")).all()
        return queryset

    def get_object(self) -> Team:
        # Get Team instance
        try:
            instance = get_object_or_404(Team, uuid=self.kwargs.get("uuid"))
        except Http404:
            raise InstanceNotFound("Team with the provided uuid doesn't exist")
        return instance

    @swagger_auto_schema(
        tags=["team-subgroups"],
        operation_summary="Create a subgroup for a team",
        responses={
            201: openapi.Response("Success", SubgroupSerializer),
            400: "Validation error",
            404: "Not found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="서브그룹 이름")
            },
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        data: dict = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(team_id=self.get_object().id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        tags=["team-subgroups"],
        operation_summary="Retrieve a subgroup from a team",
        responses={
            200: openapi.Response("Success", SubgroupSerializer),
            400: "Validation error",
            404: "Not found",
        },
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        tags=["team-subgroups"],
        operation_summary="Update a subgroup's name",
        responses={
            200: openapi.Response("Success", SubgroupSerializer),
            400: "Validation error",
            404: "Not found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="서브그룹 이름")
            },
        ),
    ),
)
@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        tags=["team-subgroups"],
        operation_summary="Delete a subgroup",
        responses={
            200: openapi.Response("Success", SubgroupSerializer),
            400: "Validation error",
            404: "Not found",
        },
    ),
)
class SubgroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubgroupSerializer
    queryset = SubGroup.objects.all()
    allowed_methods = ["PATCH", "GET", "DELETE"]

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())

    def perform_destroy(self, instance):
        TeamMemberService.delete_schedule(instance.team.name, subgroup=instance.name)
        instance.delete()
