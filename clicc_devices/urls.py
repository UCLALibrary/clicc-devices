from django.urls import path
from . import views

urlpatterns = [
    path("", views.view_sets, name="view_sets"),
    path("logs/", views.show_log, name="show_log"),
    path("logs/<int:line_count>", views.show_log, name="show_log"),
    path("release_notes/", views.release_notes, name="release_notes"),
]
