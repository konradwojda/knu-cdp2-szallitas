from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path
from transportation.gtfs_tools.gtfs_import import GTFSLoader

from . import models


class CsvImportForm(forms.Form):
    zip_import = forms.FileField()


class TransportAdminSite(admin.AdminSite):
    index_template = "admin/custom_index.html"

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("upload-zip/", self.upload_zip),
        ]
        return new_urls + urls

    def upload_zip(self, request: HttpRequest):
        if request.method == "POST":
            zip_file = request.FILES["zip_import"]
            zip_name = request.FILES["zip_import"].name

            if not zip_file.name.endswith(".zip"):
                messages.warning(request, "The wrong file type was uploaded.")
                return HttpResponseRedirect(request.path_info)

            models.Trip.objects.all().delete()
            models.PatternStop.objects.all().delete()
            models.Pattern.objects.all().delete()
            models.CalendarException.objects.all().delete()
            models.Calendar.objects.all().delete()
            models.Line.objects.all().delete()
            models.Stop.objects.all().delete()
            models.Agency.objects.all().delete()

            gtfs_loader = GTFSLoader()
            gtfs_loader.from_zip(zip_file)

            models.Import.objects.update_or_create(filename=zip_name)

            messages.success(request, "Your zip file has been uploaded")
            return redirect("..")

        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


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
