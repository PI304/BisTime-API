import unittest

from django.test import TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext
import sqlparse

from apps.team.models import Team
from apps.team.services import TeamService


class SQLQueryTest(TestCase):
    def setUp(self):
        Team.objects.create(name="Test", admin_code="000000", uuid=TeamService.generate_team_uuid(),
                            security_question=1, security_answer="wltn", start_time="09:00", end_time="20:00")

    def see_raw_sql(self):
        with CaptureQueriesContext(connection) as ctx:
            team = Team.objects.prefetch_related("subgroup_set").filter(name="Test")
            team_list = list(team)
            print(ctx.captured_queries)
            self.assertEqual(len(ctx.captured_queries), 2)


# run python3 manage.py test config.tests.tests.config.SQLQueryTest.see_raw_sql
