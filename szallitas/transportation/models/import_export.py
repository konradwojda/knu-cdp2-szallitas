from django.db import models


class Import(models.Model):
    filename = models.CharField(max_length=100, default='zipfile')
    created = models.DateTimeField(auto_now_add=True)

    # Added space before 'Imports' to change order of display in admin page
    class Meta:
        verbose_name_plural = " Imports"