from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("line/<int:line_id>/", views.line, name="line"),
    path("stop/<int:stop_id>/", views.stop, name="stop"),
    path("line_stop/<int:line_id>/<int:stop_id>/", views.line_at_stop, name="line_at_stop"),
]