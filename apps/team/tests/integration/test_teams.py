import pytest
from rest_framework.test import APIClient

from config.client_request_for_test import ClientRequest


class TestTeamEnd2End(object):
    def setup_class(cls):
        cls.request = ClientRequest(APIClient())
        cls.base_url = "/api/teams"

    @pytest.mark.django_db
    def test_get_team_by_name(self, create_team, create_subgroups):
        url = self.base_url + "?name=Team1"
        res = self.request("get", url)
        assert res.status_code == 200
        assert res.data["name"] == "Team1"
        assert len(res.data["subgroups"]) == 3

    @pytest.mark.django_db
    def test_get_team_by_uuid(self, create_team, create_subgroups):
        url = self.base_url + "/TCBSqtMWXVC22sGebhSW5QL"
        res = self.request("get", url)
        assert res.status_code == 200
        assert res.data["name"] == "Team1"
        assert len(res.data["subgroups"]) == 3
        assert set(res.data["subgroups"]) == set(
            ["subgroup1", "subgroup2", "subgroup3"]
        )

    @pytest.mark.django_db
    def test_update_team_name(self, create_team):
        url = self.base_url + "/TCBSqtMWXVC22sGebhSW5QL"
        res = self.request("patch", url, {"name": "NewTeamName1"})
        print(res.data)
        assert res.status_code == 200
        assert res.data["name"] == "NewTeamName1"

    @pytest.mark.django_db
    def test_get_subgroup_by_id(self, create_team, create_subgroups):
        url = self.base_url + "/subgroups/999"
        res = self.request("get", url)
        assert res.status_code == 200
        assert res.data["name"] == "subgroup1"

    @pytest.mark.django_db
    def test_update_subgroup_name(self, create_team, create_subgroups):
        url = self.base_url + "/subgroups/999"
        new_name = "new subgroup1"
        res = self.request("patch", url, {"name": new_name})
        assert res.status_code == 200
        assert res.data["name"] == new_name

    @pytest.mark.django_db
    def test_get_all_subgroups(self, create_team, create_subgroups):
        url = self.base_url + "/TCBSqtMWXVC22sGebhSW5QL/subgroups"
        res = self.request("get", url)
        assert res.status_code == 200
        assert res.data["count"] == 3

    @pytest.mark.django_db
    def test_verify_team_admin_code(self, create_team):
        url = self.base_url + "/TCBSqtMWXVC22sGebhSW5QL/admin/verify"
        res = self.request("post", url, {"admin_code": "3fDDXe"})
        print(res)
        assert res.status_code == 204
