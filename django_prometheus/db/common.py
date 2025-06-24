from django_prometheus.db import (
    connection_errors_total,
    connections_total,
    errors_total,
    execute_many_total,
    execute_total,
    query_duration_seconds,
)


class ExceptionCounterByType:
    """A context manager that counts exceptions by type.

    Exceptions increment the provided counter, whose last label's name
    must match the `type_label` argument.

    In other words:

    c = Counter('http_request_exceptions_total', 'Counter of exceptions',
                ['method', 'type'])
    with ExceptionCounterByType(c, extra_labels={'method': 'GET'}):
        handle_get_request()
    """

    def __init__(self, counter, type_label="type", extra_labels=None):
        self._counter = counter
        self._type_label = type_label
        self._labels = dict(extra_labels)  # Copy labels since we modify them.

    def __enter__(self):
        pass

    def __exit__(self, typ, value, traceback):
        if typ is not None:
            self._labels.update({self._type_label: typ.__name__})
            self._counter.labels(**self._labels).inc()


class DatabaseWrapperMixin:
    """Extends the DatabaseWrapper to count connections and cursors."""

    def get_new_connection(self, *args, **kwargs):
        connections_total.labels(self.alias, self.vendor).inc()
        try:
            return super().get_new_connection(*args, **kwargs)
        except Exception:
            connection_errors_total.labels(self.alias, self.vendor).inc()
            raise

    def create_cursor(self, name=None):
        return self.connection.cursor(factory=ExportingCursorWrapper(self.CURSOR_CLASS, self.alias, self.vendor))


def ExportingCursorWrapper(cursor_class, alias, vendor):
    """Returns a CursorWrapper class that knows its database's alias and
    vendor name.
    """
    labels = {"alias": alias, "vendor": vendor}

    class CursorWrapper(cursor_class):
        """Extends the base CursorWrapper to count events."""

        def execute(self, *args, **kwargs):
            execute_total.labels(alias, vendor).inc()
            with (
                query_duration_seconds.labels(**labels).time(),
                ExceptionCounterByType(errors_total, extra_labels=labels),
            ):
                return super().execute(*args, **kwargs)

        def executemany(self, query, param_list, *args, **kwargs):
            execute_total.labels(alias, vendor).inc(len(param_list))
            execute_many_total.labels(alias, vendor).inc(len(param_list))
            with (
                query_duration_seconds.labels(**labels).time(),
                ExceptionCounterByType(errors_total, extra_labels=labels),
            ):
                return super().executemany(query, param_list, *args, **kwargs)

    return CursorWrapper
