from django.urls import path

from apps.event.views import (
    EventView,
    EventUpdateView,
    EventDateView,
    ScheduleList,
    ScheduleDetail,
)

urlpatterns = [
    path("", EventView.as_view(), name="create-instant-event"),
    path("<int:pk>/", EventUpdateView.as_view(), name="update-instant-event"),
    path("<int:pk>/date/", EventDateView.as_view(), name="event-dates"),
    path("<int:pk>/schedule/", ScheduleList.as_view(), name="schedule-list"),
    path(
        "<int:pk>/schedule/<str:name>/",
        ScheduleDetail.as_view(),
        name="schedule-detail",
    ),
]
