from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Line, Pattern, PatternStop, Stop
from .timetable.tabular import generate_tabular_timetable


def index(request: HttpRequest) -> HttpResponse:
    context = {"lines": Line.objects.all()}
    return render(request, "transportation/index.html", context)


def line(request: HttpRequest, line_id: int) -> HttpResponse:
    patterns = Pattern.objects.filter(line__id=line_id)
    if not patterns:
        raise Http404("Pattern does not exist for line {}".format(line_id))

    context = {
        "line_id": line_id,
        "line": Line.objects.get(pk=line_id),
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
