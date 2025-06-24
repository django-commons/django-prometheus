from unittest.mock import MagicMock

import pytest

from django_prometheus.migrations import ExportMigrationsForDatabase
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
