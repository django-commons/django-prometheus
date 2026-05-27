import logging

from django.core.exceptions import ImproperlyConfigured
from django.db.backends.postgresql import base
from django.db.backends.postgresql.base import Cursor

from django_prometheus.db import (
    aws_failover_failed_total,
    aws_failover_success_total,
    aws_transaction_resolution_unknown_total,
    connection_errors_total,
    connections_total,
    errors_total,
    execute_many_total,
    execute_total,
    query_duration_seconds,
)
from django_prometheus.db.common import DatabaseWrapperMixin, ExceptionCounterByType

try:
    import psycopg
    from aws_advanced_python_wrapper import AwsWrapperConnection
    from aws_advanced_python_wrapper.errors import (
        FailoverFailedError,
        FailoverSuccessError,
        TransactionResolutionUnknownError,
    )
except ImportError as e:
    raise ImproperlyConfigured(
        "AWS Advanced Python Wrapper is required for this backend. "
        "Install it with: pip install aws-advanced-python-wrapper"
    ) from e

logger = logging.getLogger(__name__)


class AwsPrometheusCursor(Cursor):
    def __init__(self, connection, alias, vendor):
        super().__init__(connection)
        self.alias = alias
        self.vendor = vendor
        self._labels = {"alias": alias, "vendor": vendor}

    def execute(self, sql, params=None):
        execute_total.labels(self.alias, self.vendor).inc()
        with (
            query_duration_seconds.labels(**self._labels).time(),
            ExceptionCounterByType(errors_total, extra_labels=self._labels),
        ):
            return self._execute_with_failover_handling(sql, params)

    def executemany(self, sql, param_list):
        param_count = len(param_list) if param_list else 0
        execute_total.labels(self.alias, self.vendor).inc(param_count)
        execute_many_total.labels(self.alias, self.vendor).inc(param_count)
        with (
            query_duration_seconds.labels(**self._labels).time(),
            ExceptionCounterByType(errors_total, extra_labels=self._labels),
        ):
            return self._executemany_with_failover_handling(sql, param_list)

    def _execute_with_failover_handling(self, sql, params=None):
        try:
            return super().execute(sql, params)
        except FailoverSuccessError:
            logger.info("Database failover completed successfully, retrying query")
            aws_failover_success_total.labels(self.alias, self.vendor).inc()
            self._configure_session_state()
            return super().execute(sql, params)
        except FailoverFailedError as e:
            logger.error("Database failover failed: %s", e)
            aws_failover_failed_total.labels(self.alias, self.vendor).inc()
            raise
        except TransactionResolutionUnknownError as e:
            logger.error("Transaction resolution unknown after failover: %s", e)
            aws_transaction_resolution_unknown_total.labels(self.alias, self.vendor).inc()
            raise

    def _executemany_with_failover_handling(self, sql, param_list):
        try:
            return super().executemany(sql, param_list)
        except FailoverSuccessError:
            logger.info("Database failover completed successfully, retrying executemany")
            aws_failover_success_total.labels(self.alias, self.vendor).inc()
            self._configure_session_state()
            return super().executemany(sql, param_list)
        except FailoverFailedError as e:
            logger.error("Database failover failed during executemany: %s", e)
            aws_failover_failed_total.labels(self.alias, self.vendor).inc()
            raise
        except TransactionResolutionUnknownError as e:
            logger.error("Transaction resolution unknown during executemany: %s", e)
            aws_transaction_resolution_unknown_total.labels(self.alias, self.vendor).inc()
            raise

    def _configure_session_state(self):
        pass


class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
    def __init__(self, settings_dict, alias=None):
        super().__init__(settings_dict, alias)
        options = self.settings_dict.get("OPTIONS", {})
        self.aws_plugins = options.get("aws_plugins", "failover,host_monitoring")
        self.connect_timeout = options.get("connect_timeout", 30)
        self.socket_timeout = options.get("socket_timeout", 30)

    def get_new_connection(self, conn_params):
        connections_total.labels(self.alias, self.vendor).inc()
        try:
            host = conn_params.get("host", "localhost")
            port = conn_params.get("port", 5432)
            database = conn_params.get("database", "")
            user = conn_params.get("user", "")
            password = conn_params.get("password", "")
            options = conn_params.get("options", {})

            connection = AwsWrapperConnection.connect(
                psycopg.Connection.connect,
                host=host,
                port=port,
                dbname=database,
                user=user,
                password=password,
                plugins=self.aws_plugins,
                connect_timeout=self.connect_timeout,
                socket_timeout=self.socket_timeout,
                autocommit=False,
                **options,
            )

            connection.cursor_factory = lambda conn: AwsPrometheusCursor(conn, self.alias, self.vendor)
            logger.info("Successfully created AWS wrapper connection to %s:%s", host, port)
            return connection

        except Exception as e:
            connection_errors_total.labels(self.alias, self.vendor).inc()
            logger.error("Failed to create AWS wrapper connection: %s", e)
            raise

    def create_cursor(self, name=None):
        if name:
            cursor = self.connection.cursor(name=name)
        else:
            cursor = self.connection.cursor()
        return AwsPrometheusCursor(cursor.connection, self.alias, self.vendor)

    def _close(self):
        if self.connection is not None:
            try:
                self.connection.close()
            except Exception as e:
                logger.warning("Error closing AWS wrapper connection: %s", e)

    def is_usable(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.warning("Connection is not usable: %s", e)
            return False

    def ensure_connection(self):
        if self.connection is None:
            self.connect()
        elif not self.is_usable():
            logger.info("Connection is not usable, reconnecting...")
            self.close()
            self.connect()
