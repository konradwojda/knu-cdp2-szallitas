import traceback
from collections import defaultdict
from typing import IO, cast
from zipfile import BadZipFile

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .gtfs_tools.gtfs_export import export_all
from .gtfs_tools.gtfs_import import CalendarFileNotFound, GTFSLoader, clear_tables
from .models import Agency, Calendar, CalendarException, Line, Pattern, PatternStop, Stop, Trip
from .timetable.tabular import DepartureBoardByCalendar, generate_tabular_timetable


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

    timetable_by_header: list[tuple[str, DepartureBoardByCalendar]]

    if getattr(settings, "MERGE_TIMETABLES_BY_HEADSIGN", False):
        # FIXME: What if there are the same headsigns in two different directions?
        ps_by_headsign: defaultdict[str, list[PatternStop]] = defaultdict(list)
        for pattern in line.pattern_set.all():
            for ps in pattern.pattern_stop_set.filter(stop_id=stop_id).all():
                ps_by_headsign[pattern.headsign].append(ps)

        timetable_by_header = [
            (header, generate_tabular_timetable(*pattern_stops))
            for header, pattern_stops in ps_by_headsign.items()
        ]

    else:
        timetable_by_header = [
            (pattern.headsign, generate_tabular_timetable(pattern_stop))
            for pattern in line.pattern_set.all()
            # Skip patterns not stopping at the requested stop
            if (pattern_stop := pattern.pattern_stop_set.filter(stop_id=stop_id).first())
        ]

    context = {"line": line, "stop": stop, "timetable_by_header": timetable_by_header}
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
    export_all(cast(IO[bytes], response))
    response["Content-Disposition"] = "attachment; filename={}".format(zipfile_name)
    return response


class CsvImportForm(forms.Form):
    zip_import = forms.FileField(label="")


@login_required
@staff_member_required
def upload_zip(request: HttpRequest):
    if request.method == "POST":
        zip_file = cast(UploadedFile, request.FILES["zip_import"])

        clear_tables()

        gtfs_loader = GTFSLoader()
        try:
            gtfs_loader.from_zip(zip_file)
        except BadZipFile:
            messages.warning(request, "Bad file was uploaded.")
            return HttpResponseRedirect(request.path_info)
        except CalendarFileNotFound:
            messages.warning(request, "Calendar file was not found.")
            return HttpResponseRedirect(request.path_info)
        except Exception:
            messages.error(request, f"Exception occurred:{traceback.format_exc()}")
            return HttpResponseRedirect(request.path_info)

        messages.success(request, "Your zip file has been uploaded")
        return redirect("/admin/")

    form = CsvImportForm()
    return render(request, "admin/zip_upload.html", {"form": form})
