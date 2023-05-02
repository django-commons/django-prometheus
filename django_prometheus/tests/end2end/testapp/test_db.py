from unittest import skipUnless

from django.db import connections
from django.test import TestCase

from django_prometheus.testutils import (
    assert_metric_compare,
    assert_metric_diff,
    assert_metric_equal,
    get_metric,
    save_registry,
)


class BaseDbMetricTest(TestCase):
    # https://docs.djangoproject.com/en/2.2/topics/testing/tools/#django.test.SimpleTestCase.databases
    databases = "__all__"


@skipUnless(connections["test_db_1"].vendor == "sqlite", "Skipped unless test_db_1 uses sqlite")
class TestDbMetrics(BaseDbMetricTest):
    """Test django_prometheus.db metrics.

    Note regarding the values of metrics: many tests interact with the
    database, and the test runner itself does. As such, tests that
    require that a metric has a specific value are at best very
    fragile. Consider asserting that the value exceeds a certain
    threshold, or check by how much it increased during the test.
    """

    def test_config_has_expected_databases(self):
        """Not a real unit test: ensures that testapp.settings contains the
        databases this test expects."""
        assert "default" in connections.databases.keys()
        assert "test_db_1" in connections.databases.keys()
        assert "test_db_2" in connections.databases.keys()

    def test_counters(self):
        cursor_db1 = connections["test_db_1"].cursor()
        cursor_db2 = connections["test_db_2"].cursor()
        cursor_db1.execute("SELECT 1")
        for _ in range(200):
            cursor_db2.execute("SELECT 2")
        cursor_db1.execute("SELECT 3")
        try:
            cursor_db1.execute("this is clearly not valid SQL")
        except Exception:
            pass

        assert_metric_equal(
            1,
            "django_db_errors_total",
            alias="test_db_1",
            vendor="sqlite",
            type="OperationalError",
        )
        assert get_metric("django_db_execute_total", alias="test_db_1", vendor="sqlite") > 0
        assert get_metric("django_db_execute_total", alias="test_db_2", vendor="sqlite") >= 200

    def test_histograms(self):
        cursor_db1 = connections["test_db_1"].cursor()
        cursor_db2 = connections["test_db_2"].cursor()
        cursor_db1.execute("SELECT 1")
        for _ in range(200):
            cursor_db2.execute("SELECT 2")
        assert (
            get_metric(
                "django_db_query_duration_seconds_count",
                alias="test_db_1",
                vendor="sqlite",
            )
            > 0
        )
        assert (
            get_metric(
                "django_db_query_duration_seconds_count",
                alias="test_db_2",
                vendor="sqlite",
            )
            >= 200
        )

    def test_execute_many(self):
        registry = save_registry()
        cursor_db1 = connections["test_db_1"].cursor()
        cursor_db1.executemany(
            "INSERT INTO testapp_lawn(location) VALUES (?)",
            [("Paris",), ("New York",), ("Berlin",), ("San Francisco",)],
        )
        assert_metric_diff(
            registry,
            4,
            "django_db_execute_many_total",
            alias="test_db_1",
            vendor="sqlite",
        )


@skipUnless("postgresql" in connections, "Skipped unless postgresql database is enabled")
class TestPostgresDbMetrics(BaseDbMetricTest):
    """Test django_prometheus.db metrics for postgres backend.

    Note regarding the values of metrics: many tests interact with the
    database, and the test runner itself does. As such, tests that
    require that a metric has a specific value are at best very
    fragile. Consider asserting that the value exceeds a certain
    threshold, or check by how much it increased during the test.
    """

    def test_counters(self):
        registry = save_registry()
        cursor = connections["postgresql"].cursor()

        for _ in range(20):
            cursor.execute("SELECT 1")

        assert_metric_compare(
            registry,
            lambda a, b: a + 20 <= b < a + 25,
            "django_db_execute_total",
            alias="postgresql",
            vendor="postgresql",
        )


@skipUnless("mysql" in connections, "Skipped unless mysql database is enabled")
class TestMysDbMetrics(BaseDbMetricTest):
    """Test django_prometheus.db metrics for mys backend.

    Note regarding the values of metrics: many tests interact with the
    database, and the test runner itself does. As such, tests that
    require that a metric has a specific value are at best very
    fragile. Consider asserting that the value exceeds a certain
    threshold, or check by how much it increased during the test.
    """

    def test_counters(self):
        registry = save_registry()
        cursor = connections["mysql"].cursor()

        for _ in range(20):
            cursor.execute("SELECT 1")

        assert_metric_compare(
            registry,
            lambda a, b: a + 20 <= b < a + 25,
            "django_db_execute_total",
            alias="mysql",
            vendor="mysql",
        )


@skipUnless("postgis" in connections, "Skipped unless postgis database is enabled")
class TestPostgisDbMetrics(BaseDbMetricTest):
    """Test django_prometheus.db metrics for postgis backend.

    Note regarding the values of metrics: many tests interact with the
    database, and the test runner itself does. As such, tests that
    require that a metric has a specific value are at best very
    fragile. Consider asserting that the value exceeds a certain
    threshold, or check by how much it increased during the test.
    """

    def test_counters(self):
        r = save_registry()
        cursor = connections["postgis"].cursor()

        for _ in range(20):
            cursor.execute("SELECT 1")

        assert_metric_compare(
            r,
            lambda a, b: a + 20 <= b < a + 25,
            "django_db_execute_total",
            alias="postgis",
            vendor="postgresql",
        )
