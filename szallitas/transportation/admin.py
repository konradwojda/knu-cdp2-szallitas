from django.contrib import admin
from django.contrib import messages

from . import models
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django import forms
from django.http import HttpResponseRedirect


class CsvImportForm(forms.Form):
	csv_upload = forms.FileField()

class AgencyAdmin(admin.ModelAdmin):

	def get_urls(self):
		urls = super().get_urls()
		new_urls = [path("upload-csv/", self.upload_csv),]
		return new_urls + urls

	def upload_csv(self, request):

		if request.method == "POST":
			csv_file = request.FILES["csv_upload"]

			if not csv_file.name.endswith(".csv"):
				messages.warning(request, "The wrong file type was uploaded.")
				return HttpResponseRedirect(request.path_info)

			file_data = csv_file.read().decode("utf-8")
			csv_data = file_data.split("\n")

			for x in csv_data:
				fields = x.split(",")
				created = models.Agency.objects.update_or_create(
					name = fields[0],
    				website = fields[1],
    				timezone = fields[2],
    				telephone = fields[3],
					)
			self.message_user(request, "Your csv file has been uploaded")
			# url = reverse("admin/agency:index")
			return redirect("..")
		
		form = CsvImportForm()
		data = {"form": form}

		return render(request, "admin/csv_upload.html", data)



admin.site.register(models.Agency, AgencyAdmin)
admin.site.register(models.Calendar)
admin.site.register(models.CalendarException)
admin.site.register(models.Line)
admin.site.register(models.Stop)
admin.site.register(models.Pattern)
admin.site.register(models.PatternStop)
admin.site.register(models.Trip)
