import os

from botocore.exceptions import ClientError
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils import timezone
from dotenv import load_dotenv
from io import BytesIO
from typing import Union, List

import PIL
import shortuuid
from PIL import Image
from rest_framework.request import Request

from apps.event.services import EventService
from apps.team.models import Team, TeamRegularEvent, SubGroup, TeamMember
from config import s3_config
from config.exceptions import (
    InstanceNotFound,
    S3ImagesUploadFailed,
    InternalServerError,
)

load_dotenv()


class TeamService(object):
    def __init__(self, request: Request, team: Union[Team, None] = None):
        self.request = request
        self.team = team

    @staticmethod
    def generate_admin_code() -> str:
        admin_code: str = shortuuid.ShortUUID().random(length=6)
        return admin_code

    @staticmethod
    def generate_team_uuid() -> str:
        return "T" + EventService.generate_uuid()

    @staticmethod
    def reset_admin_code(team: Team) -> Team:
        team.admin_code = TeamService.generate_admin_code()
        team.updated_at = timezone.now()
        team.save(update_fields=["admin_code", "updated_at"])

        return team


class TeamRegularEventService(object):
    def __init__(self, request: Request, r_event: Union[TeamRegularEvent, None] = None):
        self.request = request
        self.r_event = r_event

    @staticmethod
    def generate_r_event_uuid() -> str:
        return "R" + EventService.generate_uuid()


class TeamMemberService(object):

    bucket_name = os.environ.get("S3_BUCKET_NAME")

    @staticmethod
    def create_schedule_bitmap_bytes(schedule: List[bytearray]):
        bitmap = Image.new("1", (7, 48))
        pixel_map = bitmap.load()

        for i in range(bitmap.size[0]):
            for j in range(bitmap.size[1]):
                pixel_map[i, j] = schedule[i][j]

        bitmap.tobitmap(name="image")
        print(type(bitmap))
        return bitmap

    @staticmethod
    def save_schedule(bitmap: PIL.Image.Image, team: str, name: str) -> bool:
        s3 = s3_config.s3_client_connection()

        buffer = BytesIO()
        bitmap.save(buffer, "XBM")
        buffer.seek(0)

        sent_data = s3.put_object(
            Body=buffer,
            Bucket=TeamMemberService.bucket_name,
            Key=f"Teams/{team}/{name}.xbm",
        )
        if sent_data["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise S3ImagesUploadFailed()

        return True

    @staticmethod
    def __list_chunker(target_list: list, size: int):
        for i in range(0, len(target_list), size):
            yield target_list[i : i + size]

    @staticmethod
    def get_member_schedule(team: str, name: str, s3_connection=None):

        if s3_connection:
            s3 = s3_connection
        else:
            s3 = s3_config.s3_client_connection()

        try:
            file_byte_string = s3.get_object(
                Bucket=TeamMemberService.bucket_name,
                Key=f"Teams/{team}/{name}.xbm",
            )["Body"].read()
        except ClientError:
            raise InstanceNotFound(
                "schedule for the provided information does not exist"
            )

        img = Image.open(BytesIO(file_byte_string))
        pixel_map = [int(x / 255) for x in list(img.getdata())]

        return list(TeamMemberService.__list_chunker(pixel_map, 48))

    @staticmethod
    def __get_schedules(team_name: str, members: List[TeamMember], s3_connection=None):
        if not s3_connection:
            s3 = s3_config.s3_client_connection()
        else:
            s3 = s3_connection

        schedules = []
        for m in members:
            data = {
                "name": m.name,
                "subgroup": m.subgroup.name,
                "week_schedule": TeamMemberService.get_member_schedule(
                    team_name, name=m.name, s3_connection=s3
                ),
            }
            schedules.append(data)

        return schedules

    @staticmethod
    def get_all_member_schedules(team: Team):
        members: QuerySet = team.members.all()
        return TeamMemberService.__get_schedules(team.name, members)

    @staticmethod
    def get_subgroup_schedules(team: Team, subgroup: str):
        members: QuerySet = team.members.all()
        subgroup_members: List[TeamMember] = []

        for m in members:
            if m.subgroup.name == subgroup:
                subgroup_members.append(m)

        if members is None:
            raise InstanceNotFound(
                "subgroup with the provided name does not exist in the team"
            )

        return TeamMemberService.__get_schedules(team.name, members)

    @staticmethod
    def __delete_all_object_versions(object_key: str, s3_bucket=None):
        if not s3_bucket:
            bucket = s3_config.s3_bucket()
        else:
            bucket = s3_bucket
        try:
            res = bucket.object_versions.filter(Prefix=object_key).delete()
            print(res)
            print(f"Permanently deleted all versions of object {object_key}")
        except ClientError as e:
            print(e)
            raise InternalServerError(e.MSG_TEMPLATE)

    @staticmethod
    def delete_schedule(
        team_name: str, subgroup: Union[str, None] = None, name: Union[str, None] = None
    ):
        s3_bucket = s3_config.s3_bucket()

        if subgroup:
            print(team_name, subgroup)
            try:
                members = get_list_or_404(
                    TeamMember, team__name=team_name, subgroup__name=subgroup
                )
            except Http404:
                print("no member schedules to delete from s3")
                return

            for m in members:
                object_key = f"Teams/{team_name}/{name}.xbm"
                TeamMemberService.__delete_all_object_versions(object_key, s3_bucket)

        elif not subgroup and name:
            # 한명의 스케줄 삭제
            object_key = f"Teams/{team_name}/{name}.xbm"
            TeamMemberService.__delete_all_object_versions(object_key, s3_bucket)

        elif not subgroup and not name:
            # 팀 삭제
            object_key = f"Teams/{team_name}"
            TeamMemberService.__delete_all_object_versions(object_key, s3_bucket)
