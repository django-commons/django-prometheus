import os
import time

from django.db import connections
from django.http import FileResponse
from django.shortcuts import render
from django.template.response import TemplateResponse

from testapp.models import Lawn


def index(request):
    return TemplateResponse(request, "index.html", {})


def help(request):
    # render does not instantiate a TemplateResponse, so it does not
    # increment the "by_templatename" counters.
    return render(request, "help.html", {})


def slow(request):
    """This view takes .1s to load, on purpose."""
    time.sleep(0.1)
    return TemplateResponse(request, "slow.html", {})


def newlawn(request, location):
    """This view creates a new Lawn instance in the database."""
    lawn = Lawn()
    lawn.location = location
    lawn.save()
    return TemplateResponse(request, "lawn.html", {"lawn": lawn})


class ObjectionException(Exception):
    pass


def objection(request):
    raise ObjectionException("Objection!")


def sql(request):
    databases = connections.databases.keys()
    query = request.GET.get("query")
    db = request.GET.get("database")
    if query and db:
        cursor = connections[db].cursor()
        cursor.execute(query, [])
        results = cursor.fetchall()
        return TemplateResponse(
            request,
            "sql.html",
            {"query": query, "rows": results, "databases": databases},
        )
    return TemplateResponse(request, "sql.html", {"query": None, "rows": None, "databases": databases})


def file(request):
    return FileResponse(open(os.devnull, "rb"))
