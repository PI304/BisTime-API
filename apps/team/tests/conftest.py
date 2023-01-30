import pytest

from apps.team.models import Team, SubGroup


@pytest.fixture(autouse=False, scope="function")
def create_team(db):
    Team.objects.create(
        id=999,
        admin_code="3fDDXe",
        security_question=1,
        security_answer="김선생",
        uuid="TCBSqtMWXVC22sGebhSW5QL",
        name="Team1",
        start_time="09:00",
        end_time="21:00",
    )


@pytest.fixture(autouse=False, scope="function")
def create_subgroups(db):
    SubGroup.objects.create(id=999, team_id=999, name="subgroup1")
    SubGroup.objects.create(id=998, team_id=999, name="subgroup2")
    SubGroup.objects.create(id=997, team_id=999, name="subgroup3")
