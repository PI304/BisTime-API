from django.db import models
from config.mixins import TimeStampMixin


class SecurityQuestion(TimeStampMixin):
    """
    Security questions in case of team admin code reset
    """

    id = models.BigAutoField(primary_key=True)
    question = models.CharField(max_length=200, null=False)

    class Meta:
        db_table = "security_question"

    def __str__(self) -> str:
        return f"[{self.id}] {self.question}"

    def __repr__(self) -> str:
        return f"SecurityQuestion({self.id}, {self.question})"
