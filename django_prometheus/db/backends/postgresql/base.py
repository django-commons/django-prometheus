from django.db.backends.postgresql import base

from django_prometheus.db.common import DatabaseWrapperMixin, ExportingCursorWrapper


class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
    def get_connection_params(self):
        conn_params = super().get_connection_params()
        conn_params["cursor_factory"] = ExportingCursorWrapper(conn_params["cursor_factory"], self.alias, self.vendor)
        return conn_params

    def create_cursor(self, name=None):
        # cursor_factory is set in get_connection_params() so psycopg already
        # creates instrumented cursors. Delegate to Django's implementation to
        # avoid the mixin's create_cursor which is incompatible with psycopg3.
        return base.DatabaseWrapper.create_cursor(self, name=name)
