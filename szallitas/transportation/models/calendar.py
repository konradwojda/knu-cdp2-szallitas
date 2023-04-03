from django.db import models


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


class CalendarException(models.Model):
    day = models.DateField()
    added = models.BooleanField()
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
