from typing import Any

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.team.models import Team
from apps.team.serializers import TeamSerializer
from apps.team.services import TeamService
from config.exceptions import InstanceNotFound


class TeamAdminCodeVerificationView(APIView):
    @swagger_auto_schema(
        operation_summary="Check admin code",
        tags=["team-admin"],
        responses={
            204: "No content",
            404: "Team with the provided uuid does not exist",
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        admin_code = request.data.get("admin_code")
        try:
            instance = get_object_or_404(Team, uuid=kwargs.get("uuid"))
        except Http404:
            raise InstanceNotFound("Team with the provided uuid does not exist")
        if instance.admin_code != admin_code:
            raise PermissionDenied("Wrong admin code")
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class TeamAdminCodeResetView(APIView):
    @swagger_auto_schema(
        tags=["team-admin"],
        operation_summary="Reset admin code",
        operation_description="Returns randomly generated new admin code",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["securityAnswer"],
            properties={
                "securityAnswer": openapi.Schema(
                    type=openapi.TYPE_STRING, description="보안 질문 정답"
                )
            },
        ),
        responses={
            200: openapi.Response("Success", TeamSerializer),
            404: "Team with the provided uuid does not exist",
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        security_answer = request.data.get("security_answer")
        try:
            instance = get_object_or_404(Team, uuid=kwargs.get("uuid"))
        except Http404:
            raise InstanceNotFound("Team with the provided uuid does not exist")

        if instance.security_answer != security_answer:
            raise AuthenticationFailed("Wrong answer for security question")
        else:
            updated_team = TeamService.reset_admin_code(instance)
            return Response(
                TeamSerializer(updated_team).data, status=status.HTTP_200_OK
            )
