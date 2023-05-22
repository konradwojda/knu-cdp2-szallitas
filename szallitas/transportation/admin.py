from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path
from transportation.gtfs_tools.gtfs_import import GTFSLoader

from . import models


class CsvImportForm(forms.Form):
    zip_import = forms.FileField()

class ImportAdmin(admin.ModelAdmin):
    list_display = ("filename", "created")
    
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("upload-zip/", self.upload_zip),
        ]
        return new_urls + urls
    
    def upload_zip(self, request):
        if request.method == "POST":
            zip_file = request.FILES["zip_import"]
            zip_name = request.FILES["zip_import"].name

            if not zip_file.name.endswith(".zip"):
                messages.warning(request, "The wrong file type was uploaded.")
                return HttpResponseRedirect(request.path_info)
            gtfs_loader = GTFSLoader()
            gtfs_loader.from_zip(zip_file)

            # file_data = zip_file.read().decode("utf-8")
            # csv_data = file_data.split("\n")

            # for x in csv_data:
            #     fields = x.split(",")
            #     models.Import.objects.update_or_create(
            #         filename=fields[0],
            #     )

            # self.updateModel(csv_data, request.path_info)
            models.Import.objects.update_or_create(filename=zip_name)

            self.message_user(request, "Your zip file has been uploaded")
            return redirect("..")

        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


admin.site.register(models.Agency)
admin.site.register(models.Calendar)
admin.site.register(models.CalendarException)
admin.site.register(models.Line)
admin.site.register(models.Pattern)
admin.site.register(models.PatternStop)
admin.site.register(models.Stop)
admin.site.register(models.Trip)
admin.site.register(models.Import, ImportAdmin)
