from django.db import models
from .agency import Agency


class Line(models.Model):
    class LineType(models.IntegerChoices):
        # TODO: Add descriptions
        TRAM = 0
        METRO = 1
        RAIL = 2
        BUS = 3
        FERRY = 4
        CABLE_TRAM = 5
        AERIAL_LIFT = 6
        FUNICULAR = 7
        TROLLEYBUS = 11
        MONORAIL = 12

    code = models.CharField(max_length=16)
    description = models.CharField(max_length=128, blank=True, null=True)
    type_ = models.IntegerField(choices=LineType.choices)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
