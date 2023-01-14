# Generated by Django 4.1.5 on 2023-01-14 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0007_alter_teammember_table"),
    ]

    operations = [
        migrations.AlterField(
            model_name="teammember",
            name="subgroup",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="team.subgroup",
            ),
        ),
    ]