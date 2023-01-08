from datetime import datetime
from typing import Any

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.team.models import Team, TeamRegularEvent, SubGroup
from apps.team.serializers import (
    TeamSerializer,
    TeamRegularEventSerializer,
    SubgroupSerializer,
)
from apps.team.services import TeamService, TeamRegularEventService
from config.exceptions import InstanceNotFound


class TeamCreateView(generics.CreateAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    allowed_methods = ["POST"]

    @swagger_auto_schema(
        operation_summary="Create Team",
        operation_description="Should expose admin code to user",
        responses={
            201: openapi.Response("Success", TeamSerializer),
            400: "Validation error",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "securityAnswer"],
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
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        serializer: TeamSerializer = self.get_serializer(request.data)
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
class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    allowed_methods = ["PATCH", "GET", "DELETE"]

    def get_object(self) -> Team:
        return self.queryset.filter(uuid=self.kwargs.get("uuid")).first()

    @swagger_auto_schema(
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
    )
    def perform_update(self, serializer):
        serializer.save(updated_at=datetime.now())

    @swagger_auto_schema(
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
    )
    def perform_destroy(self, instance) -> None:
        instance.delete()
        # TODO: remove all s3 bitmap images under this team


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
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
            instance = get_object_or_404(Team, id=self.kwargs.get("uuid"))
        except Http404:
            raise InstanceNotFound("Team with the provided uuid doesn't exist")
        return instance

    @swagger_auto_schema(
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
        data["team"] = associated_team.id
        serializer = self.get_serializer(data)
        if serializer.is_valid(raises_exception=True):
            serializer.save(uuid=TeamRegularEventService.generate_r_event_uuid())

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
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
        operation_summary="Delete a regular event of a team",
        responses={
            204: "No content",
            404: "Not found",
        },
    ),
)
class TeamRegularEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamRegularEventSerializer
    queryset = TeamRegularEvent.objects.all()
    allowed_methods = ["GET", "PATCH", "DELETE"]

    def get_object(self) -> TeamRegularEvent:
        return self.queryset.filter(uuid=self.kwargs.get("uuid")).first()

    @swagger_auto_schema(
        operation_summary="Create regular event for a team",
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
    )
    def perform_update(self, serializer):
        serializer.save(updated_at=datetime.now())


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Get subgroups of a team",
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
            instance = get_object_or_404(Team, id=self.kwargs.get("uuid"))
        except Http404:
            raise InstanceNotFound("Team with the provided uuid doesn't exist")
        return instance

    @swagger_auto_schema(
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
        data["team"] = self.get_object().id
        serializer = self.get_serializer(data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubgroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubgroupSerializer
    queryset = SubGroup.objects.all()
    allowed_methods = ["PATCH", "GET", "DELETE"]

    def perform_update(self, serializer):
        serializer.save(updated_at=datetime.now())
        # TODO: change s3 directory name

    def perform_destroy(self, instance):
        instance.delete()
        # TODO: remove s3 bucket bitmaps under this subgroup


class TeamAdminCodeVerificationView(APIView):
    @swagger_auto_schema(
        operation_summary="Check admin code",
        operation_description="Place admin code input value in 'Authorization' header using 'Basic' scheme",
        responses={
            201: "No content",
            404: "Team with the provided uuid does not exist",
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if (
            request.headers["Authorization"]
            and len(request.headers["Authorization"].split(" ")) == 2
        ):
            admin_code = request.headers["Authorization"].split(" ")[1]
            try:
                instance = get_object_or_404(Team, uuid=kwargs.get("uuid"))
            except Http404:
                raise InstanceNotFound("Team with the provided uuid does not exist")

            if instance.admin_code != admin_code:
                raise PermissionDenied("Wrong admin code")
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError(
                "Wrongly configured Authorization header. Use 'Basic' scheme."
            )
