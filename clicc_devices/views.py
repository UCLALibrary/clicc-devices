from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from clicc_devices.models import Set, Item


def default_view(request: HttpRequest) -> HttpResponse:
    return render(request, "base.html")


def show_log(request: HttpRequest, line_count: int = 200) -> HttpResponse:
    """Display log file in the browser.

    :param request: The HTTP request object.
    :param line_count: The most recent lines in the log. If not provided, shows the whole log.
    :return: Rendered HTML for the logs.
    """
    log_file = settings.LOG_FILE
    try:
        with open(log_file, "r") as f:
            # Get just the last line_count lines in the log.
            lines = f.readlines()[-line_count:]
            # Template prints these as a single block, so join lines into one chunk.
            log_data = "".join(lines)
    except FileNotFoundError:
        log_data = f"Log file {log_file} not found"

    return render(request, "log.html", {"log_data": log_data})


def release_notes(request: HttpRequest) -> HttpResponse:
    """Display release notes.

    :param request: The HTTP request object.
    :return: Rendered HTML for the release notes.
    """
    return render(request, "release_notes.html")


@login_required
def view_sets(request: HttpRequest) -> HttpResponse:
    """Display all available Sets.

    :param request: The HTTP request object.
    :return: Rendered HTML for the Sets.
    """

    all_sets = Set.objects.all().order_by("name")
    set_data = []
    for s in all_sets:
        set_data.append(
            {
                "name": s.name,
                "unit": s.unit,
                "type": s.type.name,
                "retrieved": s.retrieved,
                "item_count": Item.objects.filter(set=s).count(),
            }
        )

    return render(request, "view_sets.html", {"set_data": set_data})
