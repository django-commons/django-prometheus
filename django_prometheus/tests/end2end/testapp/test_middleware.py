import pytest

from django_prometheus.testutils import (
    assert_metric_diff,
    assert_metric_equal,
    save_registry,
)
from testapp.views import ObjectionException


def M(metric_name):
    """Makes a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return f"django_http_{metric_name}"


def T(metric_name):
    """Makes a full metric name from a short metric name like M(metric_name)

    This method adds a '_total' postfix for metrics.
    """
    return f"{M(metric_name)}_total"


class TestMiddlewareMetrics:
    """Test django_prometheus.middleware.

    Note that counters related to exceptions can't be tested as
    Django's test Client only simulates requests and the exception
    handling flow is very different in that simulation.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, settings):
        settings.PROMETHEUS_LATENCY_BUCKETS = (0.05, 1.0, 2.0, 4.0, 5.0, 10.0, float("inf"))

    def test_request_counters(self, client):
        registry = save_registry()
        client.get("/")
        client.get("/")
        client.get("/help")
        client.post("/", {"test": "data"})

        assert_metric_diff(registry, 4, M("requests_before_middlewares_total"))
        assert_metric_diff(registry, 4, M("responses_before_middlewares_total"))
        assert_metric_diff(registry, 3, T("requests_total_by_method"), method="GET")
        assert_metric_diff(registry, 1, T("requests_total_by_method"), method="POST")
        assert_metric_diff(registry, 4, T("requests_total_by_transport"), transport="http")
        assert_metric_diff(
            registry,
            2,
            T("requests_total_by_view_transport_method"),
            view="testapp.views.index",
            transport="http",
            method="GET",
        )
        assert_metric_diff(
            registry,
            1,
            T("requests_total_by_view_transport_method"),
            view="testapp.views.help",
            transport="http",
            method="GET",
        )
        assert_metric_diff(
            registry,
            1,
            T("requests_total_by_view_transport_method"),
            view="testapp.views.index",
            transport="http",
            method="POST",
        )
        # We have 3 requests with no post body, and one with a few
        # bytes, but buckets are cumulative so that is 4 requests with
        # <=128 bytes bodies.
        assert_metric_diff(registry, 3, M("requests_body_total_bytes_bucket"), le="0.0")
        assert_metric_diff(registry, 4, M("requests_body_total_bytes_bucket"), le="128.0")
        assert_metric_equal(None, M("responses_total_by_templatename"), templatename="help.html")
        assert_metric_diff(registry, 3, T("responses_total_by_templatename"), templatename="index.html")
        assert_metric_diff(registry, 4, T("responses_total_by_status"), status="200")
        assert_metric_diff(registry, 0, M("responses_body_total_bytes_bucket"), le="0.0")
        assert_metric_diff(registry, 3, M("responses_body_total_bytes_bucket"), le="128.0")
        assert_metric_diff(registry, 4, M("responses_body_total_bytes_bucket"), le="8192.0")
        assert_metric_diff(registry, 4, T("responses_total_by_charset"), charset="utf-8")
        assert_metric_diff(registry, 0, M("responses_streaming_total"))

    def test_latency_histograms(self, client):
        # Caution: this test is timing-based. This is not ideal. It
        # runs slowly (each request to /slow takes at least .1 seconds
        # to complete), to eliminate flakiness we adjust the buckets used
        # in the test suite.

        registry = save_registry()

        # This always takes more than .1 second, so checking the lower
        # buckets is fine.
        client.get("/slow")
        assert_metric_diff(
            registry,
            0,
            M("requests_latency_seconds_by_view_method_bucket"),
            le="0.05",
            view="slow",
            method="GET",
        )
        assert_metric_diff(
            registry,
            1,
            M("requests_latency_seconds_by_view_method_bucket"),
            le="5.0",
            view="slow",
            method="GET",
        )

    def test_exception_latency_histograms(self, client):
        registry = save_registry()

        try:
            client.get("/objection")
        except ObjectionException:
            pass
        assert_metric_diff(
            registry,
            2,
            M("requests_latency_seconds_by_view_method_bucket"),
            le="2.5",
            view="testapp.views.objection",
            method="GET",
        )

    def test_streaming_responses(self, client):
        registry = save_registry()
        client.get("/")
        client.get("/file")
        assert_metric_diff(registry, 1, M("responses_streaming_total"))
        assert_metric_diff(registry, 1, M("responses_body_total_bytes_bucket"), le="+Inf")
