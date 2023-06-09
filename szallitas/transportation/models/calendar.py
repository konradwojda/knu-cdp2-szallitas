from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from django.db.models import Manager

    from .trip import Trip


class Calendar(models.Model):
    name = models.CharField(max_length=64)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()

    # Attributes generated by Django, but which need explicit hints for type checker:
    id: int
    pk: int
    calendar_exception_set: "Manager[CalendarException]"
    trip_set: "Manager[Trip]"


class CalendarException(models.Model):
    day = models.DateField()
    added = models.BooleanField()
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)

    class Meta:
        default_related_name = "calendar_exception_set"
        constraints = [
            models.UniqueConstraint(
                fields=["calendar", "day"],
                name="Only one CalendarException for a calendar on a given day",
            )
        ]

    # Attributes generated by Django, but which need explicit hints for type checker:
    id: int
    pk: int
    calendar_id: int
