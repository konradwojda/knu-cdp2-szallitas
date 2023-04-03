from django.db import models

class Stop(models.Model):

    class WheelchairAccessibility(models.IntegerChoices):
        NO_INFO = 0
        ACCESSIBLE = 1
        NOT_ACCESSIBLE = 2

    name = models.CharField(max_length=64)
    code = models.CharField(max_length=16, null=True, blank=True)
    lat = models.DecimalField()
    lon = models.DecimalField()
    wheelchair_accessible = models.IntegerField(choices=WheelchairAccessibility.choices)
