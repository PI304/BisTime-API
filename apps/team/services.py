import os

from botocore.exceptions import ClientError
from django.shortcuts import get_list_or_404
from dotenv import load_dotenv
from io import BytesIO
from typing import Union, List

import PIL
import shortuuid
from PIL import Image
from rest_framework.request import Request

from apps.event.services import EventService
from apps.team.models import Team, TeamRegularEvent, SubGroup
from config import s3_config
from config.exceptions import InstanceNotFound

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


class TeamRegularEventService(object):
    def __init__(self, request: Request, r_event: Union[TeamRegularEvent, None] = None):
        self.request = request
        self.r_event = r_event

    @staticmethod
    def generate_r_event_uuid() -> str:
        return "R" + EventService.generate_uuid()


class SubGroupService:
    @staticmethod
    def delete_s3_subgroup(name: str) -> None:
        pass


class S3ImagesUploadFailed(Exception):
    pass


class TeamMemberFixedScheduleService(object):

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
    def save_schedule(
        bitmap: PIL.Image.Image, team: str, name: str, subgroup: str = "default"
    ) -> bool:
        s3 = s3_config.s3_connection()

        buffer = BytesIO()
        bitmap.save(buffer, "XBM")
        buffer.seek(0)

        sent_data = s3.put_object(
            Body=buffer,
            Bucket=TeamMemberFixedScheduleService.bucket_name,
            Key=f"Teams/{team}/{subgroup}/{name}.xbm",
        )
        if sent_data["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise S3ImagesUploadFailed("Failed to upload image to bucket")

        return True

    @staticmethod
    def __list_chunker(target_list: list, size: int):
        for i in range(0, len(target_list), size):
            yield target_list[i : i + size]

    @staticmethod
    def get_member_schedule(
        team: str, name: str, subgroup: str = "default", s3_connection=None
    ):

        if s3_connection:
            s3 = s3_connection
        else:
            s3 = s3_config.s3_connection()

        try:
            file_byte_string = s3.get_object(
                Bucket=TeamMemberFixedScheduleService.bucket_name,
                Key=f"Teams/{team}/{subgroup}/{name}.xbm",
            )["Body"].read()
        except ClientError:
            raise InstanceNotFound(
                "schedule for the provided information does not exist"
            )

        img = Image.open(BytesIO(file_byte_string))
        pixel_map = [int(x / 255) for x in list(img.getdata())]

        return list(TeamMemberFixedScheduleService.__list_chunker(pixel_map, 48))

    @staticmethod
    def get_all_member_schedules(team: str):
        s3 = s3_config.s3_connection()

        schedules = []

        objects = s3.list_objects_v2(
            Bucket=TeamMemberFixedScheduleService.bucket_name, Prefix=f"Teams/{team}/"
        )

        for obj in objects["Contents"]:
            if obj["Key"].endswith(".xbm"):
                subgroup = obj["Key"].split("/")[2]
                name = obj["Key"].split("/")[3].split(".")[0]

                data = {
                    "name": name,
                    "subgroup": subgroup,
                    "week_schedule": TeamMemberFixedScheduleService.get_member_schedule(
                        team, name=name, subgroup=subgroup, s3_connection=s3
                    ),
                }
                schedules.append(data)

        return schedules

    @staticmethod
    def get_subgroup_schedules(team: str, subgroup: str):
        s3 = s3_config.s3_connection()

        schedules = []

        objects = s3.list_objects_v2(
            Bucket=TeamMemberFixedScheduleService.bucket_name,
            Prefix=f"Teams/{team}/{subgroup}/",
        )

        for obj in objects["Contents"]:
            if obj["Key"].endswith(".xbm"):
                name = obj["Key"].split("/")[3].split(".")[0]

                data = {
                    "name": name,
                    "subgroup": subgroup,
                    "week_schedule": TeamMemberFixedScheduleService.get_member_schedule(
                        team, name=name, subgroup=subgroup, s3_connection=s3
                    ),
                }
                schedules.append(data)

        return schedules

    @staticmethod
    def delete_schedule():
        pass
