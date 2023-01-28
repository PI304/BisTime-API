from django.urls import path

from apps.event.views import (
    EventView,
    EventDateView,
    EventDateDestroyView,
    EventDetailView,
    ScheduleView,
    ScheduleDestroyView,
)

urlpatterns = [
    path("", EventView.as_view(), name="event-list"),
    path("/<str:uuid>", EventDetailView.as_view(), name="event-detail"),
    path("/<str:uuid>/dates", EventDateView.as_view(), name="event-dates-list"),
    path("/dates/<int:pk>", EventDateDestroyView.as_view(), name="dates-detail"),
    path("/<str:uuid>/schedules", ScheduleView.as_view(), name="schedule-list"),
    path(
        "/<str:uuid>/schedules/<str:name>",
        ScheduleDestroyView.as_view(),
        name="user-schedule-list",
    ),
]
