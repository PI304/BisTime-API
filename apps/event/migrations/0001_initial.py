# Generated by Django 4.1.5 on 2023-03-01 14:12

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("team", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
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
                        help_text="이벤트를 구분하거나, url 생성을 위한 uuid 문자열",
                        max_length=22,
                        validators=[django.core.validators.MinLengthValidator(22)],
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                (
                    "associated_team",
                    models.ForeignKey(
                        help_text="이벤트를 생성한 팀",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event",
                        to="team.team",
                    ),
                ),
            ],
            options={
                "db_table": "event",
            },
        ),
        migrations.CreateModel(
            name="EventDate",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("date", models.DateField()),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_date",
                        to="event.event",
                    ),
                ),
            ],
            options={
                "db_table": "event_date",
            },
        ),
        migrations.CreateModel(
            name="Schedule",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=50)),
                (
                    "availability",
                    models.BinaryField(help_text="길이 48인 array 를 bytearray 로 변환하여 저장"),
                ),
                (
                    "date",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_date",
                        to="event.eventdate",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedule",
                        to="event.event",
                    ),
                ),
            ],
            options={
                "db_table": "schedule",
                "unique_together": {("name", "event", "date")},
            },
        ),
    ]
