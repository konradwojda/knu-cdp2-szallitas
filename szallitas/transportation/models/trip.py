from django.db import models

from .calendar import Calendar
from .pattern import Pattern
from .stop import WheelchairAccessibility


class Trip(models.Model):
    wheelchair_accessible = models.IntegerField(choices=WheelchairAccessibility.choices)
    departure = models.IntegerField(max_length=6)
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
