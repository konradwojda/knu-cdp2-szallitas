from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from transportation.gtfs_tools.gtfs_export import export_all
from transportation.gtfs_tools.gtfs_import import GTFSLoader

from .models import Agency, Calendar, CalendarException, Line, Pattern, PatternStop, Stop, Trip
from .timetable.tabular import generate_tabular_timetable


def index(request: HttpRequest) -> HttpResponse:
    context = {"lines": Line.objects.all()}
    return render(request, "transportation/index.html", context)


def line(request: HttpRequest, line_id: int) -> HttpResponse:
    line = get_object_or_404(Line, pk=line_id)
    patterns = Pattern.objects.filter(line__id=line_id)

    context = {
        "line": line,
        "patterns": patterns,
    }
    return render(request, "transportation/line.html", context)


def stop(request: HttpRequest, stop_id: int) -> HttpResponse:
    stop = get_object_or_404(Stop, id=stop_id)

    context = {"lines": Line.objects.filter(pattern__stops__id=stop_id).distinct(), "stop": stop}
    return render(request, "transportation/stop.html", context)


def timetable(request: HttpRequest, line_id: int, stop_id: int) -> HttpResponse:
    # FIXME: What if pattern stops multiple times at the stop?
    line = get_object_or_404(Line, pk=line_id)
    stop = get_object_or_404(Stop, pk=stop_id)
    timetable_by_pattern = [
        (pattern, generate_tabular_timetable(pattern_stop))
        for pattern in line.pattern_set.all()
        # Skip patterns not stopping at the requested stop
        if (pattern_stop := pattern.pattern_stop_set.filter(stop_id=stop_id).first())
    ]

    context = {"line": line, "stop": stop, "timetable_by_pattern": timetable_by_pattern}
    return render(request, "transportation/timetable.html", context)


def stops(request: HttpRequest) -> JsonResponse:
    return JsonResponse(list(Stop.objects.all().values()), safe=False)


def lines(request: HttpRequest) -> JsonResponse:
    return JsonResponse(list(Line.objects.all().values()), safe=False)


@login_required
@staff_member_required
def download(request: HttpRequest):
    zipfile_name = "szallitas-gtfs.zip"
    response = HttpResponse(content_type="application/zip")
    export_all(response)
    response["Content-Disposition"] = "attachment; filename={}".format(zipfile_name)
    return response


class CsvImportForm(forms.Form):
    zip_import = forms.FileField()


@login_required
@staff_member_required
def uploadzip(request: HttpRequest):
    if request.method == "POST":
        zip_file = UploadedFile(request.FILES["zip_import"])
        zip_name = str(zip_file.name)

        if not zip_name.endswith(".zip"):
            messages.warning(request, "The wrong file type was uploaded.")
            return HttpResponseRedirect(request.path_info)

        Trip.objects.all().delete()
        PatternStop.objects.all().delete()
        Pattern.objects.all().delete()
        CalendarException.objects.all().delete()
        Calendar.objects.all().delete()
        Line.objects.all().delete()
        Stop.objects.all().delete()
        Agency.objects.all().delete()

        gtfs_loader = GTFSLoader()
        gtfs_loader.from_zip(zip_file)

        messages.success(request, "Your zip file has been uploaded")
        return redirect("/admin/")

    form = CsvImportForm()
    data = {"form": form}
    return render(request, "admin/csv_upload.html", data)
