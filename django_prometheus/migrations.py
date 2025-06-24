from django.db import connections
from django.db.backends.dummy.base import DatabaseWrapper
from prometheus_client import Gauge

from django_prometheus.conf import NAMESPACE

unapplied_migrations = Gauge(
    "django_migrations_unapplied_total",
    "Count of unapplied migrations by database connection",
    ["connection"],
    namespace=NAMESPACE,
)

applied_migrations = Gauge(
    "django_migrations_applied_total",
    "Count of applied migrations by database connection",
    ["connection"],
    namespace=NAMESPACE,
)


def ExportMigrationsForDatabase(alias, executor):
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    unapplied_migrations.labels(alias).set(len(plan))
    applied_migrations.labels(alias).set(len(executor.loader.applied_migrations))


def ExportMigrations():
    """Exports counts of unapplied migrations.

    This is meant to be called during app startup, ideally by
    django_prometheus.apps.AppConfig.
    """
    # Import MigrationExecutor lazily. MigrationExecutor checks at
    # import time that the apps are ready, and they are not when
    # django_prometheus is imported. ExportMigrations() should be
    # called in AppConfig.ready(), which signals that all apps are
    # ready.
    from django.db.migrations.executor import MigrationExecutor

    if "default" in connections and (isinstance(connections["default"], DatabaseWrapper)):
        # This is the case where DATABASES = {} in the configuration,
        # i.e. the user is not using any databases. Django "helpfully"
        # adds a dummy database and then throws when you try to
        # actually use it. So we don't do anything, because trying to
        # export stats would crash the app on startup.
        return
    for alias in connections.databases:
        executor = MigrationExecutor(connections[alias])
        ExportMigrationsForDatabase(alias, executor)
