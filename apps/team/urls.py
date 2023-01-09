from django.urls import path, include
from .views import (
    TeamCreateView,
    TeamDetailView,
    TeamRegularEventListView,
    TeamRegularEventDetailView,
    SubgroupListView,
    SubgroupDetailView,
    TeamAdminCodeVerificationView,
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
        "/<str:uuid>/regular-events",
        TeamRegularEventListView.as_view(),
        name="team-events-list",
    ),
    path(
        "/regular-events/<str:uuid>",
        TeamRegularEventDetailView.as_view(),
        name="team-events-detail",
    ),
    path("/<str:uuid>/subgroups", SubgroupListView.as_view(), name="subgroups-create"),
    path(
        "/subgroups/<int:pk>",
        SubgroupDetailView.as_view(),
        name="subgroup-detail",
    ),
]
