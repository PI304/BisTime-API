from django.db import models
from django.core.validators import MinLengthValidator
from config.mixins import TimeStampMixin, TimeBlockMixin


class Team(TimeStampMixin):
    """
    For team mode
    """

    class SecurityQuestion(models.IntegerChoices):
        HIGH_SCHOOL_TEACHER = 0, "고등학교 1학년 때의 수학 선생님의 성함은 무엇인가요?"
        CUSTOM = 1, "직접 입력"

    id = models.BigAutoField(primary_key=True)
    uuid = models.CharField(
        max_length=23,
        null=False,
        help_text="팀을 구분하거나, 팀 뷰 url 생성을 위한 uuid 문자열",
    )
    name = models.CharField(max_length=100, null=False)
    admin_code = models.CharField(max_length=6, null=False)
    security_question = models.BigIntegerField(
        null=False,
        choices=SecurityQuestion.choices,
        default=SecurityQuestion.HIGH_SCHOOL_TEACHER,
    )
    custom_security_question = models.CharField(max_length=200, null=True)
    security_answer = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "team"

    def __str__(self) -> str:
        return f"[{self.id}] {self.name}"

    def __repr__(self) -> str:
        return f"Team({self.id}, {self.name})"


class TeamRegularEvent(TimeStampMixin, TimeBlockMixin):
    """
    Regular team events
    """

    class DayOfWeek(models.IntegerChoices):
        MON = (0, "MON")
        TUE = (1, "TUE")
        WED = (2, "WED")
        THU = (3, "THU")
        FRI = (4, "FRI")
        SAT = (5, "SAT")
        SUN = (6, "SUN")

    id = models.BigAutoField(primary_key=True)
    uuid = models.CharField(max_length=23, null=False)
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=200, null=False, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_event")
    day = models.IntegerField(choices=DayOfWeek.choices, null=False)

    def get_day_of_week(self, day_of_week: str) -> DayOfWeek:
        return self.DayOfWeek[day_of_week]

    class Meta:
        db_table = "team_regular_event"

    def __str__(self) -> str:
        return f"[{self.id}] {self.title} (team_id: {self.team_id}"

    def __repr__(self) -> str:
        return f"RegularEvent({self.id}, {self.title})"


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
        return f"[{self.id}] {self.name} (team_id: {self.team_id}"

    def __repr__(self) -> str:
        return f"SubGroup({self.id}, {self.team}, {self.name})"
