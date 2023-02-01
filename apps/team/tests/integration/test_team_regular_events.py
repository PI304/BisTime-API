import pytest

from config.client_request_for_test import ClientRequest
from rest_framework.test import APIClient


class TestTeamRegularEventEnd2End(object):
    def setup_class(cls):
        cls.request = ClientRequest(APIClient())
        cls.base_url = "/api/teams/"
        cls.test_team_uuid = "TCBSqtMWXVC22sGebhSW5QL"
        cls.test_event_uuid = "RHA3UGKv6L8Vt8uovm5MhYt"

    @pytest.mark.django_db
    def test_get_all_team_regular_events(self, create_team, create_regular_events):
        url = self.base_url + self.test_team_uuid + "/regular-events"
        res = self.request("get", url)

        assert res.status_code == 200
        assert res.data["count"] == 2

    @pytest.mark.django_db
    def test_retrieve_team_regular_events(self, create_team, create_regular_events):
        url = self.base_url + "regular-events/" + self.test_event_uuid
        res = self.request("get", url)

        assert res.status_code == 200
        assert res.data["uuid"] == self.test_event_uuid

    @pytest.mark.django_db
    def test_update_regular_event(self, create_team, create_regular_events):
        url = self.base_url + "regular-events/" + self.test_event_uuid
        new_team_data = dict(title="new title", start_time="15:00")
        res = self.request("patch", url, new_team_data)
        assert res.status_code == 200
        assert res.data["title"] == new_team_data["title"]
        assert res.data["start_time"] == new_team_data["start_time"]
