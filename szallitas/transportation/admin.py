from django.contrib import admin
from django.contrib.auth.models import User


from . import models


class TransportAdminSite(admin.AdminSite):
    index_template = "admin/custom_index.html"

class CustomUserAdmin(admin.ModelAdmin):
    # Set user permissions here
    pass


admin_site = TransportAdminSite(name="TransportAdminSite")


admin_site.register(User, CustomUserAdmin)
admin_site.register(models.Agency)
admin_site.register(models.Calendar)
admin_site.register(models.CalendarException)
admin_site.register(models.Line)
admin_site.register(models.Pattern)
admin_site.register(models.PatternStop)
admin_site.register(models.Stop)
admin_site.register(models.Trip)
