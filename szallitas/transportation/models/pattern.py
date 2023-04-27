from typing import TYPE_CHECKING

from django.db import models

from .line import Line
from .stop import Stop

if TYPE_CHECKING:
    from django.db.models import Manager

    from .trip import Trip


class Pattern(models.Model):
    class Direction(models.IntegerChoices):
        INBOUND = 0
        OUTBOUND = 1

    headsign = models.CharField(max_length=64)
    direction = models.IntegerField(choices=Direction.choices, null=True, blank=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    stops = models.ManyToManyField[Stop, "PatternStop"](Stop, through="PatternStop")

    # Attributes generated by Django, but which need explicit hints for type checker
    id: int
    pk: int
    line_id: int
    pattern_stop_set: "Manager[PatternStop]"
    trip_set: "Manager[Trip]"


class PatternStop(models.Model):
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    travel_time = models.DurationField()
    index = models.SmallIntegerField()

    class Meta:
        default_related_name = "pattern_stop_set"

    # Attributes generated by Django, but which need explicit hints for type checker
    id: int
    pk: int
    pattern_id: int
    stop_id: int
