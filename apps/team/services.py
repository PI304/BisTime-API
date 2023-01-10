from io import BytesIO
from typing import Union, List

import PIL
import shortuuid
from PIL import Image
from rest_framework.request import Request

from apps.event.services import EventService
from apps.team.models import Team, TeamRegularEvent
from config import s3_config


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


class TeamMemberFixedScheduleService:
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
            Body=buffer, Bucket="bistime-s3", Key=f"Teams/{team}/{subgroup}/{name}.xbm"
        )
        if sent_data["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise S3ImagesUploadFailed("Failed to upload image to bucket")

        return True

    @staticmethod
    def get_member_schedule(team: str, name: str, subgroup: str = "default"):
        s3 = s3_config.s3_connection()

        file_byte_string = s3.get_object(
            Bucket="bistime-s3", Key=f"Teams/{team}/{subgroup}/{name}.xbm"
        )["Body"].read()
        img = Image.open(BytesIO(file_byte_string))
        img.show()
        print(img.tobytes())
        return img.tobytes()

    @staticmethod
    def delete_schedule():
        pass
