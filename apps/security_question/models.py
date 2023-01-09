from django.db import models

from apps.team.models import Team
from config.mixins import TimeStampMixin


class TeamSecurityQuestion(TimeStampMixin):
    """
    Security questions in case of team admin code reset
    """

    class SecurityQuestion(models.TextChoices):
        HIGH_SCHOOL_TEACHER = "고등학교 1학년 때의 수학 선생님의 성함은 무엇인가요?"
        CUSTOM = "직접 입력"

    id = models.BigAutoField(primary_key=True)
    question = models.CharField(
        max_length=200,
        null=False,
        choices=SecurityQuestion.choices,
        default=SecurityQuestion.HIGH_SCHOOL_TEACHER,
    )
    custom_question = models.CharField(max_length=200, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    answer = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "team_security_question"

    def __str__(self) -> str:
        return f"[{self.id}] {self.question}"

    def __repr__(self) -> str:
        return f"TeamSecurityQuestion({self.id}, {self.question})"
