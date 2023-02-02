import pytest

from apps.team.models import Team
from apps.team.services import TeamService


class TestTeamServices:
    """
    unit tests for team app service layer
    """

    @pytest.mark.django_db
    def test_team_reset_admin_code(self, create_team):
        team = Team.objects.get(id=999)
        old_admin_code = team.admin_code
        updated_team = TeamService.reset_admin_code(team)
        new_admin_code = updated_team.admin_code

        assert old_admin_code != new_admin_code
