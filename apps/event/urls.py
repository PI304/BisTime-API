from django.urls import path

from apps.event.views import (
    EventView,
    EventRetrieveView,
    EventDateView,
    EventDateDestroyView,
    EventDetailView,
    UserScheduleView,
    ScheduleView,
)

urlpatterns = [
    path("", EventView.as_view(), name="event-list"),
    path("<str:uuid>/", EventDetailView.as_view(), name="event-detail"),
    path("<str:uuid>/", EventRetrieveView.as_view(), name="event-retrieval"),
    path("<str:uuid>/dates/", EventDateView.as_view(), name="event-dates-list"),
    path("dates/<int:pk>/", EventDateDestroyView.as_view(), name="dates-detail"),
    path("<str:uuid>/schedules/", ScheduleView.as_view(), name="schedule-list"),
    path(
        "<str:uuid>/user-schedules/",
        UserScheduleView.as_view(),
        name="user-schedule-list",
    ),
]
