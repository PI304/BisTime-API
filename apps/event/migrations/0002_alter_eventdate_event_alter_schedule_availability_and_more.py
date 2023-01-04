# Generated by Django 4.1.3 on 2022-12-22 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("event", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventdate",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="event",
                to="event.event",
            ),
        ),
        migrations.AlterField(
            model_name="schedule",
            name="availability",
            field=models.BinaryField(),
        ),
        migrations.AlterField(
            model_name="schedule",
            name="date",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="event.eventdate"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="schedule",
            unique_together={("name", "event", "date")},
        ),
    ]