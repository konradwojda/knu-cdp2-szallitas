from django.db import models


class Agency(models.Model):
    name = models.CharField(max_length=64)
    website = models.CharField(max_length=128)
    timezone = models.CharField(max_length=64, null=True, blank=True)
    telephone = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Agencies "
