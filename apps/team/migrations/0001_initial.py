# Generated by Django 4.1.5 on 2023-03-01 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SubGroup",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=50)),
            ],
            options={
                "db_table": "subgroup",
            },
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "start_time",
                    models.CharField(default="00:00", help_text="HH:MM", max_length=5),
                ),
                (
                    "end_time",
                    models.CharField(default="24:00", help_text="HH:MM", max_length=5),
                ),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "uuid",
                    models.CharField(
                        help_text="팀을 구분하거나, 팀 뷰 url 생성을 위한 uuid 문자열", max_length=23
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("admin_code", models.CharField(max_length=6)),
                (
                    "security_question",
                    models.BigIntegerField(
                        choices=[
                            (0, "직접 입력"),
                            (1, "고등학교 1학년 때의 수학 선생님의 성함은 무엇인가요?"),
                            (2, "친가 쪽 사촌 중 나이가 가장 어린 사람의 이름은 무엇인가요?"),
                            (3, "가장 오랫동안 키웠던 애완동물의 이름은 무엇인가요?"),
                        ],
                        default=1,
                    ),
                ),
                (
                    "custom_security_question",
                    models.CharField(max_length=200, null=True),
                ),
                ("security_answer", models.CharField(max_length=50)),
            ],
            options={
                "db_table": "team",
            },
        ),
        migrations.CreateModel(
            name="TeamRegularEvent",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "start_time",
                    models.CharField(default="00:00", help_text="HH:MM", max_length=5),
                ),
                (
                    "end_time",
                    models.CharField(default="24:00", help_text="HH:MM", max_length=5),
                ),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("uuid", models.CharField(max_length=23)),
                ("title", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "day",
                    models.IntegerField(
                        choices=[
                            (0, "MON"),
                            (1, "TUE"),
                            (2, "WED"),
                            (3, "THU"),
                            (4, "FRI"),
                            (5, "SAT"),
                            (6, "SUN"),
                        ]
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_regular_event",
                        to="team.team",
                    ),
                ),
            ],
            options={
                "db_table": "team_regular_event",
            },
        ),
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=20)),
                (
                    "subgroup",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="team.subgroup",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="team.team",
                    ),
                ),
            ],
            options={
                "db_table": "team_member",
            },
        ),
        migrations.AddField(
            model_name="subgroup",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subgroups",
                to="team.team",
            ),
        ),
    ]
