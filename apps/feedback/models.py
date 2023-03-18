from django.db import models

from config.mixins import TimeStampMixin


class Feedback(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    content = models.CharField(max_length=500, null=False)

    class Meta:
        db_table = "feedback"

    def __str__(self) -> str:
        return f"[{self.id}]"

    def __repr__(self) -> str:
        return f"Feedback({self.id})"
