import pytest
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.generics import get_object_or_404

from apps.team.models import Team
from apps.team.serializers import TeamSerializer


class TestTeamQueries:
    """
    Tests for assuming number of queries for a certain logic
    """

    def test_retrieve_team_queries(
        self, create_team, create_subgroups, django_assert_num_queries
    ):
        with django_assert_num_queries(2) as captured:
            queryset = Team.objects.prefetch_related("subgroups").filter(
                uuid="TCBSqtMWXVC22sGebhSW5QL"
            )
            instance = queryset.first()
            serializer = TeamSerializer(instance)
            data = serializer.data

    def test_updating_team_queries(self, create_team, create_subgroups):
        from django.db import connection, close_old_connections

        with CaptureQueriesContext(connection) as (expected_num_query):
            queryset = Team.objects.prefetch_related("subgroups").filter(
                uuid="TCBSqtMWXVC22sGebhSW5QL"
            )
            filter_kwargs = {"uuid": "TCBSqtMWXVC22sGebhSW5QL"}
            instance = get_object_or_404(queryset, **filter_kwargs)
            serializer = TeamSerializer(
                instance, data={"name": "NewTeamName"}, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save(updated_at=timezone.now())

            d = serializer.data

            # queryset 에서 2개, unique name check, update 문
            assert len(expected_num_query.captured_queries) == 4
