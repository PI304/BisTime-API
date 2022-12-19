from django.urls import path

from apps.event.views import (
    EventView,
    EventUpdateView,
    EventDateView,
    ScheduleView,
    UserScheduleView,
    BulkCreateUserScheduleView,
)

urlpatterns = [
    path("", EventView.as_view(), name="event-list"),
    path("<int:pk>/", EventUpdateView.as_view(), name="event-detail"),
    path("<int:pk>/dates/", EventDateView.as_view(), name="event-dates"),
    path("<int:pk>/schedules/", ScheduleView.as_view(), name="schedule-list"),
    path(
        "<int:pk>/schedules/<str:name>/",
        UserScheduleView.as_view(),
        name="user-schedule-list",
    ),
    path(
        "<int:pk>/schedules/<str:name>/bulk",
        BulkCreateUserScheduleView.as_view(),
        name="bulk-create-user-schedule",
    ),
]
