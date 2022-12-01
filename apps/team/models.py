from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from apps.security_question.models import SecurityQuestion
from config.mixins import TimeStampMixin, TimeBlockMixin


class Team(TimeStampMixin):
    """
    For team mode
    """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    admin_code = models.CharField(
        max_length=6, validators=[MinLengthValidator(6)], null=False
    )
    security_question = models.ForeignKey(
        SecurityQuestion, on_delete=models.DO_NOTHING, related_name="team"
    )
    security_answer = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "team"

    def __str__(self) -> str:
        return f"[{self.id}] {self.name}"

    def __repr__(self) -> str:
        return f"Team({self.id}, {self.name})"


class TeamEvent(TimeStampMixin, TimeBlockMixin):
    """
    Regular team events
    """

    class DayOfWeek(models.IntegerChoices):
        MON = 0, _("Monday")
        TUE = 1, _("Tuesday")
        WED = 2, _("Wednesday")
        THU = 3, _("Thursday")
        FRI = 4, _("Friday")
        SAT = 5, _("Saturday")
        SUN = 6, _("Sunday")

    id = models.BigAutoField(primary_key=True)
    uuid = models.CharField(
        max_length=22, validators=[MinLengthValidator(22)], null=False
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_event")
    day = models.IntegerField(choices=DayOfWeek.choices, null=False)

    def get_day_of_week(self, day_of_week: str) -> DayOfWeek:
        return self.DayOfWeek[day_of_week]


class SubGroup(TimeStampMixin):
    """
    Subgroups in a team
    """

    id = models.BigAutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "subgroup"

    def __str__(self) -> str:
        return f"[{self.id}] Team: {self.team}, {self.name}"

    def __repr__(self) -> str:
        return f"SubGroup({self.id}, {self.team}, {self.name})"
