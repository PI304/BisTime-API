from django.urls import path

from apps.team.views.fixed_schedule_views import (
    TeamMemberFixedScheduleListView,
    TeamMemberFixedScheduleDetailView,
)
from apps.team.views.views import (
    TeamCreateView,
    TeamDetailView,
    TeamRegularEventListView,
    TeamRegularEventDetailView,
    SubgroupListView,
    SubgroupDetailView,
    TeamAdminCodeVerificationView,
    TeamAdminCodeResetView,
)

urlpatterns = [
    path("/", TeamCreateView.as_view(), name="team-create"),
    path("/<str:uuid>", TeamDetailView.as_view(), name="team-detail"),
    path(
        "/<str:uuid>/admin/verify",
        TeamAdminCodeVerificationView.as_view(),
        name="code-verification",
    ),
    path(
        "/<str:uuid>/admin/reset",
        TeamAdminCodeResetView.as_view(),
        name="code-reset",
    ),
    path(
        "/<str:uuid>/regular-events",
        TeamRegularEventListView.as_view(),
        name="team-events-list",
    ),
    path("/<str:uuid>/subgroups", SubgroupListView.as_view(), name="subgroup-create"),
    path(
        "/<str:uuid>/fixed-schedules",
        TeamMemberFixedScheduleListView.as_view(),
        name="fixed-schedule-list",
    ),
    path(
        "/fixed-schedules/<str:name>",
        TeamMemberFixedScheduleDetailView.as_view(),
        name="fixed-schedule-detail",
    ),
    path(
        "/regular-events/<str:uuid>",
        TeamRegularEventDetailView.as_view(),
        name="team-events-detail",
    ),
    path(
        "/subgroups/<int:pk>",
        SubgroupDetailView.as_view(),
        name="subgroup-detail",
    ),
]
