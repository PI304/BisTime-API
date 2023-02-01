from django.db import models
from rest_framework.exceptions import ValidationError


class TimeStampMixin(models.Model):
    """
    Abstract timestamp mixin base model for created_at, updated_at field
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TimeBlockMixin(models.Model):
    """
    Sets the start time and end time
    """

    start_time = models.CharField(
        max_length=5, null=False, default="00:00", help_text="HH:MM"
    )
    end_time = models.CharField(
        max_length=5, null=False, default="24:00", help_text="HH:MM"
    )

    class Meta:
        abstract = True

    @staticmethod
    def __time_validation(time_exp: str) -> None:
        if ":" not in time_exp or len(time_exp) != 5 or len(time_exp.split(":")) != 2:
            raise ValidationError("_time should be of 'HH:MM' format")

        time_split = time_exp.split(":")

        if len(time_split[0]) != 2 or len(time_split[1]) != 2:
            raise ValidationError("_time should be of 'HH:MM' format")

        if int(time_split[0]) < 0 or int(time_split[0]) > 24:
            raise ValidationError("hours should be between 00 ~ 24")

        if not (time_split[1] == "30" or time_split[1] == "00"):
            raise ValidationError("minutes should be 00 or 30")

    @staticmethod
    def validate_time_data(data: dict) -> None:
        TimeBlockMixin.__time_validation(data["start_time"])
        TimeBlockMixin.__time_validation(data["end_time"])
        if (
            int(data["end_time"].split(":")[0]) - int(data["start_time"].split(":")[0])
            < 0
        ):
            raise ValidationError("end_time should be larger than start_time")
