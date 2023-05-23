from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig

class TransportAdminConfig(AdminConfig):
    default_site = "transportation.admin.TransportAdminSite"

class TransportationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "transportation"
