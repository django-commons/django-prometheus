from django.contrib.gis.db.backends.spatialite import base, features
from django.db.backends.sqlite3 import base as sqlite_base

from django_prometheus.db.common import DatabaseWrapperMixin


class DatabaseFeatures(features.DatabaseFeatures):
    """Our database has the exact same features as the base one."""


class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
    CURSOR_CLASS = sqlite_base.SQLiteCursorWrapper
