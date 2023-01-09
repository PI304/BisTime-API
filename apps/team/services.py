from typing import Union

import shortuuid
from rest_framework.request import Request

from apps.event.services import EventService
from apps.team.models import Team, TeamRegularEvent


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
