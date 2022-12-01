from django.db import models


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
