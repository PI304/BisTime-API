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
    path("", TeamCreateView.as_view(), name="team-create"),
    path("<int:pk>", TeamDetailView.as_view(), name="team-detail"),
    path(
        "<int:pk>/events/", TeamRegularEventListView.as_view(), name="team-events-list"
    ),
    path(
        "<int:pk>/events/<int:event_id>",
        TeamRegularEventDetailView.as_view(),
        name="team-events-detail",
    ),
    path("<int:pk>/subgroups/", SubgroupListView.as_view(), name="subgroups-create"),
    path(
        "<int:pk>/subgroups/<int:subgroup_id>/",
        SubgroupDetailView.as_view(),
        name="subgroups-create",
    ),
]
