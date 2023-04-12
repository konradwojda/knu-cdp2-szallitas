from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models.agency import Agency
from .models.line import Line
from .models.stop import Stop


def index(request: HttpRequest) -> HttpResponse:
    agency = Agency(name="Metro Warszawskie", website="metro.waw.pl")
    line1 = Line(id=1, code="M1", line_type=1, agency=agency)
    line2 = Line(id=2, code="M2", line_type=1, agency=agency)
    stop1 = Stop(id=1, name="Stop1", lat=0, lon=0, wheelchair_accessible=0)
    # TODO: provide Line.objects.all()
    context = {"lines": [line1, line2], "stops": [stop1]}
    return render(request, "transportation/index.html", context)


def line(request: HttpRequest, line_id: int) -> HttpResponse:
    context = {"line_id": line_id}
    return render(request, "transportation/line.html", context)


def stop(request: HttpRequest, stop_id: int) -> HttpResponse:
    context = {"stop_id": stop_id}
    return render(request, "transportation/stop.html", context)


def timetable(request: HttpRequest, line_id: int, stop_id: int) -> HttpResponse:
    context = {"stop_id": stop_id, "line_id": line_id}
    return render(request, "transportation/timetable.html", context)
