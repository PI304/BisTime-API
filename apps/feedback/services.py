from django.db.models import QuerySet
from django.shortcuts import get_list_or_404
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from apps.feedback.models import Feedback


class FeedbackExportService(object):
    def __init__(self):
        self.workbook = None
        self.worksheet = None

    def _create_worksheet_template(self):
        wb: Workbook = Workbook()
        self.workbook = wb
        ws: Worksheet = wb.active
        self.worksheet = ws

        base_col = ["내용", "날짜"]
        self.worksheet.append(base_col)

    def _add_rows(self):
        feedbacks: list[Feedback] = get_list_or_404(Feedback)

        for feedback in feedbacks:
            self.worksheet.append([feedback.content, feedback.created_at])

    def export_feedbacks(self):
        self._create_worksheet_template()
        self._add_rows()

        return self.workbook
