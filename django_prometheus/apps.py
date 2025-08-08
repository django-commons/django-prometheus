from django.apps import AppConfig
from django.conf import settings
import sys

import django_prometheus
from django_prometheus.exports import SetupPrometheusExportsFromConfig
from django_prometheus.migrations import ExportMigrations


class DjangoPrometheusConfig(AppConfig):
    name = django_prometheus.__name__
    verbose_name = "Django-Prometheus"

    def ready(self):
        """Initializes the Prometheus exports if they are enabled in the config.

        Note that this is called even for other management commands
        than `runserver`. As such, it is possible to scrape the
        metrics of a running `manage.py test` or of another command,
        which shouldn't be done for real monitoring (since these jobs
        are usually short-lived), but can be useful for debugging.
        """
        if "manage.py" in sys.argv[0] or "django-admin" in sys.argv:
            # Avoid exports when running management commands
            return

        SetupPrometheusExportsFromConfig()
        if getattr(settings, "PROMETHEUS_EXPORT_MIGRATIONS", False):
            ExportMigrations()
