from django.db import models
from .stop import WheelchairAccessibility
from .pattern import Pattern


class Trip(models.Model):
    wheelchair_accessible = models.IntegerField(choices=WheelchairAccessibility.choices)
    departure = models.IntegerField(max_length=6)
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE)
