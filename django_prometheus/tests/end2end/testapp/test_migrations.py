from unittest.mock import MagicMock, patch

import pytest

from django_prometheus.migrations import ExportMigrations, ExportMigrationsForDatabase
from django_prometheus.testutils import assert_metric_equal


def M(metric_name):
    """Make a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return f"django_migrations_{metric_name}"


@pytest.mark.django_db
class TestMigrations:
    """Test migration counters."""

    def test_counters(self):
        executor = MagicMock()
        executor.migration_plan = MagicMock()
        executor.migration_plan.return_value = set()
        executor.loader.applied_migrations = {"a", "b", "c"}
        ExportMigrationsForDatabase("fakedb1", executor)
        assert executor.migration_plan.call_count == 1
        executor.migration_plan = MagicMock()
        executor.migration_plan.return_value = {"a"}
        executor.loader.applied_migrations = {"b", "c"}
        ExportMigrationsForDatabase("fakedb2", executor)

        assert_metric_equal(3, M("applied_total"), connection="fakedb1")
        assert_metric_equal(0, M("unapplied_total"), connection="fakedb1")
        assert_metric_equal(2, M("applied_total"), connection="fakedb2")
        assert_metric_equal(1, M("unapplied_total"), connection="fakedb2")


class TestExportMigrations:
    """Test ExportMigrations function with mocked connections."""

    @patch("django_prometheus.migrations.connections")
    @patch("django.db.migrations.executor.MigrationExecutor")
    def test_export_migrations_with_real_database(self, mock_executor_class, mock_connections):
        """Test ExportMigrations with a non-empty database connection."""

        # Create a mock connection that is NOT a DatabaseWrapper (dummy)
        mock_connections.databases = {"default": {}}
        mock_connection = MagicMock()
        mock_connection.__class__.__name__ = "RealDatabaseWrapper"
        mock_connections.__getitem__.return_value = mock_connection

        executor = MagicMock()
        executor.migration_plan.return_value = ["migration1", "migration2"]
        executor.loader.applied_migrations = {"m1", "m2", "m3"}
        mock_executor_class.return_value = executor

        ExportMigrations()

        # Verify MigrationExecutor was called with the connection
        mock_executor_class.assert_called_once_with(mock_connection)
        assert executor.migration_plan.call_count == 1

    @patch("django_prometheus.migrations.connections")
    @patch("django.db.migrations.executor.MigrationExecutor")
    def test_export_migrations_skips_dummy_database(self, mock_executor_class, mock_connections):
        """Test ExportMigrations skips dummy database (DATABASES = {} case)."""
        from django.db.backends.dummy.base import DatabaseWrapper

        # Create a mock connection that IS a DatabaseWrapper (dummy)
        mock_connections.databases = {"default": {}}
        mock_dummy_connection = MagicMock(spec=DatabaseWrapper)
        mock_connections.__getitem__.return_value = mock_dummy_connection

        ExportMigrations()

        # Verify MigrationExecutor was NOT called (because we skip dummy databases)
        mock_executor_class.assert_not_called()

    @patch("django_prometheus.migrations.connections")
    @patch("django.db.migrations.executor.MigrationExecutor")
    def test_export_migrations_with_multiple_databases(self, mock_executor_class, mock_connections):
        """Test ExportMigrations with multiple databases including a dummy one."""
        from django.db.backends.dummy.base import DatabaseWrapper

        mock_connections.databases = {"default": {}, "secondary": {}}

        mock_dummy_connection = MagicMock(spec=DatabaseWrapper)
        mock_real_connection = MagicMock()
        mock_real_connection.__class__.__name__ = "RealDatabaseWrapper"

        # Setup the connections dict to return different connections for different aliases
        def get_connection(alias):
            if alias == "default":
                return mock_dummy_connection
            else:
                return mock_real_connection

        mock_connections.__getitem__.side_effect = get_connection

        executor = MagicMock()
        executor.migration_plan.return_value = []
        executor.loader.applied_migrations = set()
        mock_executor_class.return_value = executor

        ExportMigrations()

        # Verify MigrationExecutor was called only once (for the non-dummy database)
        mock_executor_class.assert_called_once_with(mock_real_connection)
