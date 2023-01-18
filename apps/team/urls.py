from django.urls import path

from apps.team.views.admin_views import (
    TeamAdminCodeVerificationView,
    TeamAdminCodeResetView,
)
from apps.team.views.member_views import (
    TeamMemberCreateView,
    TeamMemberListView,
    TeamMemberDetailView,
)
from apps.team.views.views import (
    TeamView,
    TeamDetailView,
    TeamRegularEventListView,
    TeamRegularEventDetailView,
    SubgroupListView,
    SubgroupDetailView,
)

urlpatterns = [
    path("", TeamView.as_view(), name="team-list-create"),
    path(
        "/members",
        TeamMemberCreateView.as_view(),
        name="create-member",
    ),
    path(
        "/members/<int:pk>",
        TeamMemberDetailView.as_view(),
        name="member-detail",
    ),
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
        "/<str:uuid>/members",
        TeamMemberListView.as_view(),
        name="member-list",
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
