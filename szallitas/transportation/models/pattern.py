from django.db import models

from .line import Line
from .stop import Stop


class Pattern(models.Model):
    class Direction(models.IntegerChoices):
        INBOUND = 0
        OUTBOUND = 1

    headsign = models.CharField(max_length=64)
    direction = models.IntegerField(choices=Direction.choices, null=True, blank=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    stops: "models.ManyToManyField[Stop, PatternStop]" = models.ManyToManyField(
        Stop, through="PatternStop"
    )


class PatternStop(models.Model):
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    travel_time = models.PositiveSmallIntegerField()
    index = models.SmallIntegerField()
