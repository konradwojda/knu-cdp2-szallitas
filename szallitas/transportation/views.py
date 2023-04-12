from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .models.agency import Agency
from .models.line import Line
from .models.stop import Stop


def index(request: HttpRequest) -> HttpResponse:
    # agency = Agency(name="Metro Warszawskie", website="metro.waw.pl")
    agency = Agency.objects.create(name="Metro Warszawskie", website="metro.waw.pl")
    line1 = Line.objects.create(code="M1", line_type=1, agency=agency)
    line2 = Line.objects.create(code="M2", line_type=1, agency=agency)
    stop1 = Stop.objects.create(name="Stop1", lat=52.2, lon=21.01, wheelchair_accessible=0)
    stop1 = Stop.objects.create(name="Stop1", lat=52.34, lon=22.02, wheelchair_accessible=0)
    stop1 = Stop.objects.create(name="Stop1", lat=50.2, lon=20.04, wheelchair_accessible=0)
    stop1 = Stop.objects.create(name="Stop1", lat=53, lon=24.4, wheelchair_accessible=0)
    stop1 = Stop.objects.create(name="Stop1", lat=52, lon=20, wheelchair_accessible=0)
    stop1 = Stop.objects.create(name="Stop1", lat=52, lon=21, wheelchair_accessible=0)
    stop1 = Stop.objects.create(name="Stop1", lat=55.05, lon=23, wheelchair_accessible=0)
    stop1 = Stop.objects.create(name="Stop1", lat=50, lon=20, wheelchair_accessible=0)
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


def stops(request: HttpRequest) -> JsonResponse:
    return JsonResponse(list(Stop.objects.all().values()), safe=False)


def lines(request: HttpRequest) -> JsonResponse:
    return JsonResponse(list(Line.objects.all().values()), safe=False)
