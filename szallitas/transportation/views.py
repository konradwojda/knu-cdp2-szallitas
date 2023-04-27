from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render

from .models import Line, Pattern, Stop


def index(request: HttpRequest) -> HttpResponse:
    context = {"lines": Line.objects.all()}
    return render(request, "transportation/index.html", context)


def line(request: HttpRequest, line_id: int) -> HttpResponse:
    context = {"line_id": line_id}
    return render(request, "transportation/line.html", context)


def stop(request: HttpRequest, stop_id: int) -> HttpResponse:
    context = {"stop_id": stop_id}
    return render(request, "transportation/stop.html", context)


def timetable(request: HttpRequest, line_id: int, stop_id: int) -> HttpResponse:
    line = get_object_or_404(Line, pk=line_id)
    stop = get_object_or_404(Stop, pk=stop_id)
    patterns = get_list_or_404(Pattern, line__id=line_id)

    context = {"line": line, "stop": stop, "patterns": patterns}
    return render(request, "transportation/timetable.html", context)


def stops(request: HttpRequest) -> JsonResponse:
    return JsonResponse(list(Stop.objects.all().values()), safe=False)


def lines(request: HttpRequest) -> JsonResponse:
    return JsonResponse(list(Line.objects.all().values()), safe=False)
