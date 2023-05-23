from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("line/<int:line_id>/", views.line, name="line"),
    path("stop/<int:stop_id>/", views.stop, name="stop"),
    path("timetable/<int:line_id>/<int:stop_id>/", views.timetable, name="line_at_stop"),
    path("api/stops", views.stops, name="stops"),
    path("api/lines", views.lines, name="lines"),
    path("download_gtfs/", views.download, name="download_gtfs"),
]
