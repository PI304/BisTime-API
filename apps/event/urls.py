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
    path("<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("<str:uuid>/", EventRetrieveView.as_view(), name="event-retrieval"),
    path("<int:pk>/dates/", EventDateView.as_view(), name="event-dates-list"),
    path("dates/<int:pk>/", EventDateDestroyView.as_view(), name="dates-detail"),
    path("<int:pk>/schedules/", ScheduleView.as_view(), name="schedule-list"),
    path(
        "<int:pk>/schedules/<str:name>/",
        UserScheduleView.as_view(),
        name="user-schedule-list",
    ),
]
