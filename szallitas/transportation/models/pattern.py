from django.db import models
from .line import Line
from .stop import Stop


class PatternStop(models.Model):
    travel_time = models.PositiveSmallIntegerField(max_length=6)
    index = models.SmallIntegerField(max_length=6)


class Pattern(models.Model):
    class Direction(models.IntegerChoices):
        INBOUND = 0
        OUTBOUND = 1

    headsign = models.CharField(max_length=64)
    direction = models.IntegerField(choices=Direction.choices, null=True, blank=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    stops = models.ManyToManyField(Stop, through=PatternStop)
