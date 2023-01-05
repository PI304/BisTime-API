from django.urls import path, include
from .views import (
    TeamCreateView,
    TeamDetailView,
    TeamRegularEventListView,
    TeamRegularEventDetailView,
    SubgroupListView,
    SubgroupDetailView,
)

urlpatterns = [
    path("/", TeamCreateView.as_view(), name="team-create"),
    path("/<int:pk>", TeamDetailView.as_view(), name="team-detail"),
    path(
        "/<int:pk>/regular-events",
        TeamRegularEventListView.as_view(),
        name="team-events-list",
    ),
    path(
        "/regular-events/<int:pk>",
        TeamRegularEventDetailView.as_view(),
        name="team-events-detail",
    ),
    path("/<int:pk>/subgroups", SubgroupListView.as_view(), name="subgroups-create"),
    path(
        "/subgroups/<int:pk>/",
        SubgroupDetailView.as_view(),
        name="subgroup-detail",
    ),
]
