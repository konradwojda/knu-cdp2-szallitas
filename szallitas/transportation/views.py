from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import loader


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "transportation/index.html")


def line(request: HttpRequest, line_id: int) -> HttpResponse:
    context = {"line_id": line_id}
    return render(request, "transportation/line.html", context)


def stop(request: HttpRequest, stop_id: int) -> HttpResponse:
    context = {"stop_id": stop_id}
    return render(request, "transportation/stop.html", context)


def line_at_stop(request: HttpRequest, line_id: int, stop_id: int) -> HttpResponse:
    context = {"stop_id": stop_id, "line_id": line_id}
    return render(request, "transportation/line_stop.html", context)
