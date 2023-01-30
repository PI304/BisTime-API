import pytest
from rest_framework.test import APIClient

from apps.event.models import EventDate
from config.client_request_for_test import ClientRequest


class TestEventView(object):
    def setup_class(cls):
        cls.request = ClientRequest(APIClient())

    def test_event_get_all(self, create_event):
        url = "/api/events"
        res = self.request("get", url)
        assert res.status_code == 200
        assert res.data["count"] == 2
        assert len(res.data["results"]) == 2

    def test_event_get_one(self, create_event):
        url = "/api/events/89PKcffHuwBA9uCnGWraNZ"
        res = self.request("get", url)
        assert res.status_code == 200
        assert res.data["title"] == "test event 2"

    def test_event_add_dates(self, create_event, create_event_dates):
        url = "/api/events/dbWUg9io46UXYNsiJrPhfR/dates"
        data = {"additionalDates": ["2023-02-24", "2023-02-25"]}

        res = self.request("post", url, data)
        assert res.status_code == 201
        assert res.data["count"] == 5

    def test_event_delete(self, create_event, create_event_dates):
        url = "/api/events/dbWUg9io46UXYNsiJrPhfR"
        res = self.request("del", url)
        cascading_delete = EventDate.objects.filter(
            event__uuid="dbWUg9io46UXYNsiJrPhfR"
        )

        assert res.status_code == 204
        assert len(cascading_delete) == 0
