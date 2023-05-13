from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path

from . import models


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

			self.updateModel(csv_data, request.path_info)
			
			self.message_user(request, "Your csv file has been uploaded")
			# url = reverse("admin/agency:index")
			return redirect("..")
		
		form = CsvImportForm()
		data = {"form": form}

		return render(request, "admin/csv_upload.html", data)


class CalendarAdmin(admin.ModelAdmin):

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
				created = models.Calendar.objects.update_or_create(
					name = fields[0],
    				start_date = fields[1],
    				end_date = fields[2],
    				monday = fields[3],
					tuesday = fields[4],
					wednesday = fields[5],
					thursday = fields[6],
					friday = fields[7],
					saturday = fields[8],
					sunday = fields[9],
					)

			self.updateModel(csv_data, request.path_info)
			
			self.message_user(request, "Your csv file has been uploaded")
			return redirect("..")
		
		form = CsvImportForm()
		data = {"form": form}

		return render(request, "admin/csv_upload.html", data)
	

class CalendarExceptionAdmin(admin.ModelAdmin):

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
				created = models.CalendarException.objects.update_or_create(
					day = fields[0],
    				added = fields[1],
    				calendar = fields[2],
					)

			self.updateModel(csv_data, request.path_info)
			
			self.message_user(request, "Your csv file has been uploaded")
			return redirect("..")
		
		form = CsvImportForm()
		data = {"form": form}

		return render(request, "admin/csv_upload.html", data)
	

class LineAdmin(admin.ModelAdmin):

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
				created = models.Line.objects.update_or_create(
					code = fields[0],
    				description = fields[1],
    				line_type = fields[2],
    				agency = fields[3],
					)

			self.updateModel(csv_data, request.path_info)
			
			self.message_user(request, "Your csv file has been uploaded")
			return redirect("..")
		
		form = CsvImportForm()
		data = {"form": form}

		return render(request, "admin/csv_upload.html", data)
	
class PatternAdmin(admin.ModelAdmin):

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
				created = models.Pattern.objects.update_or_create(
					headsign = fields[0],
					direction = fields[1],
					line = fields[2],
					stops = fields[3],
					)

			self.updateModel(csv_data, request.path_info)
			
			self.message_user(request, "Your csv file has been uploaded")
			return redirect("..")
		
		form = CsvImportForm()
		data = {"form": form}

		return render(request, "admin/csv_upload.html", data)


class PatternStopAdmin(admin.ModelAdmin):

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
				created = models.PatternStop.objects.update_or_create(
					pattern = fields[0],
					stop = fields[1],
					travel_time = fields[2],
					index = fields[3],
					)

			self.updateModel(csv_data, request.path_info)
			
			self.message_user(request, "Your csv file has been uploaded")
			return redirect("..")
		
		form = CsvImportForm()
		data = {"form": form}

		return render(request, "admin/csv_upload.html", data)


class StopAdmin(admin.ModelAdmin):

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
				created = models.Stop.objects.update_or_create(
					code = fields[0],
    				description = fields[1],
    				line_type = fields[2],
    				agency = fields[3],
					)

			self.updateModel(csv_data, request.path_info)
			
			self.message_user(request, "Your csv file has been uploaded")
			return redirect("..")
		
		form = CsvImportForm()
		data = {"form": form}

		return render(request, "admin/csv_upload.html", data)
	
class TripAdmin(admin.ModelAdmin):

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
				created = models.Trip.objects.update_or_create(
					wheelchair_accessible = fields[0],
					pattern = fields[1],
					calendar = fields[2],
					)

			self.updateModel(csv_data, request.path_info)
			
			self.message_user(request, "Your csv file has been uploaded")
			return redirect("..")
		
		form = CsvImportForm()
		data = {"form": form}

		return render(request, "admin/csv_upload.html", data)

admin.site.register(models.Agency, AgencyAdmin)
admin.site.register(models.Calendar, CalendarAdmin)
admin.site.register(models.CalendarException, CalendarExceptionAdmin)
admin.site.register(models.Line, LineAdmin)
admin.site.register(models.Pattern, PatternAdmin)
admin.site.register(models.PatternStop, PatternStopAdmin)
admin.site.register(models.Stop, StopAdmin)
admin.site.register(models.Trip, TripAdmin)
