from django.urls import path

from apps.event.views import (
    EventView,
    EventUpdateView,
    EventDateView,
    ScheduleList,
    ScheduleDetail,
)

urlpatterns = [
    path("", EventView.as_view(), name="event-list"),
    path("<int:pk>/", EventUpdateView.as_view(), name="event-detail"),
    path("<int:pk>/dates/", EventDateView.as_view(), name="event-dates"),
    path("<int:pk>/schedules/", ScheduleList.as_view(), name="schedule-list"),
    path(
        "<int:pk>/schedules/<str:name>/",
        ScheduleDetail.as_view(),
        name="schedule-detail",
    ),
]
