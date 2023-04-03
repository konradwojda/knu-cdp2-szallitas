from django.contrib import admin

from . import models

admin.site.register(models.Agency)
admin.site.register(models.Calendar)
admin.site.register(models.CalendarException)
admin.site.register(models.Line)
admin.site.register(models.Stop)
admin.site.register(models.Pattern)
admin.site.register(models.PatternStop)
admin.site.register(models.Trip)
