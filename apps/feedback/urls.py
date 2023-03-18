from django.urls import path

from apps.feedback.views import FeedbackCreateView, FeedbackDownloadView

urlpatterns = [
    path("", FeedbackCreateView.as_view(), name="feedback-create"),
    path("/download", FeedbackDownloadView.as_view(), name="feedback-download"),
]
