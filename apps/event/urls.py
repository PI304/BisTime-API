from django.urls import path

from apps.event.views import (
    EventView,
    EventDateView,
    ScheduleList,
    ScheduleDetail,
    EventDateDestroyView,
    EventDetailView,
)

urlpatterns = [
    path("", EventView.as_view(), name="event-list"),
    path("<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("<int:pk>/dates/", EventDateView.as_view(), name="event-dates"),
    path("dates/<int:date_id>", EventDateDestroyView.as_view(), name="dates-detail"),
    path("<int:pk>/schedules/", ScheduleList.as_view(), name="schedule-list"),
    path(
        "<int:pk>/schedules/<str:name>/",
        ScheduleDetail.as_view(),
        name="schedule-detail",
    ),
]
