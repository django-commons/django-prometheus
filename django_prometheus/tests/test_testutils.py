#!/usr/bin/env python
from operator import itemgetter

import prometheus_client
import pytest

from django_prometheus.testutils import (
    assert_metric_diff,
    assert_metric_equal,
    assert_metric_no_diff,
    assert_metric_not_equal,
    get_metric,
    get_metric_from_frozen_registry,
    get_metrics_vector,
    save_registry,
)


class TestPrometheusTestCaseMixin:
    @pytest.fixture
    def registry(self):
        return prometheus_client.CollectorRegistry()

    @pytest.fixture(autouse=True)
    def some_gauge(self, registry):
        some_gauge = prometheus_client.Gauge("some_gauge", "Some gauge.", registry=registry)
        some_gauge.set(42)
        return some_gauge

    @pytest.fixture(autouse=True)
    def some_labelled_gauge(self, registry):
        some_labelled_gauge = prometheus_client.Gauge(
            "some_labelled_gauge",
            "Some labelled gauge.",
            ["labelred", "labelblue"],
            registry=registry,
        )
        some_labelled_gauge.labels("pink", "indigo").set(1)
        some_labelled_gauge.labels("pink", "royal").set(2)
        some_labelled_gauge.labels("carmin", "indigo").set(3)
        some_labelled_gauge.labels("carmin", "royal").set(4)
        return some_labelled_gauge

    def test_get_metric(self, registry):
        """Tests get_metric."""
        assert get_metric("some_gauge", registry=registry) == 42
        assert (
            get_metric(
                "some_labelled_gauge",
                registry=registry,
                labelred="pink",
                labelblue="indigo",
            )
            == 1
        )

    def test_get_metrics_vector(self, registry):
        """Tests get_metrics_vector."""
        vector = get_metrics_vector("some_nonexistent_gauge", registry=registry)
        assert vector == []
        vector = get_metrics_vector("some_gauge", registry=registry)
        assert vector == [({}, 42)]
        vector = get_metrics_vector("some_labelled_gauge", registry=registry)
        assert sorted(
            [
                ({"labelred": "pink", "labelblue": "indigo"}, 1),
                ({"labelred": "pink", "labelblue": "royal"}, 2),
                ({"labelred": "carmin", "labelblue": "indigo"}, 3),
                ({"labelred": "carmin", "labelblue": "royal"}, 4),
            ],
            key=itemgetter(1),
        ) == sorted(vector, key=itemgetter(1))

    def test_assert_metric_equal(self, registry):
        """Tests assert_metric_equal."""
        # First we test that a scalar metric can be tested.
        assert_metric_equal(42, "some_gauge", registry=registry)

        assert_metric_not_equal(43, "some_gauge", registry=registry)

        # Here we test that assert_metric_equal fails on nonexistent gauges.
        assert_metric_not_equal(42, "some_nonexistent_gauge", registry=registry)

        # Here we test that labelled metrics can be tested.
        assert_metric_equal(
            1,
            "some_labelled_gauge",
            registry=registry,
            labelred="pink",
            labelblue="indigo",
        )

        assert_metric_not_equal(
            1,
            "some_labelled_gauge",
            registry=registry,
            labelred="tomato",
            labelblue="sky",
        )

    def test_registry_saving(self, registry, some_gauge, some_labelled_gauge):
        """Tests save_registry and frozen registries operations."""
        frozen_registry = save_registry(registry=registry)
        # Test that we can manipulate a frozen scalar metric.
        assert get_metric_from_frozen_registry("some_gauge", frozen_registry) == 42
        some_gauge.set(99)
        assert get_metric_from_frozen_registry("some_gauge", frozen_registry) == 42
        assert_metric_diff(frozen_registry, 99 - 42, "some_gauge", registry=registry)
        assert_metric_no_diff(frozen_registry, 1, "some_gauge", registry=registry)
        # Now test the same thing with a labelled metric.
        assert (
            get_metric_from_frozen_registry(
                "some_labelled_gauge",
                frozen_registry,
                labelred="pink",
                labelblue="indigo",
            )
            == 1
        )
        some_labelled_gauge.labels("pink", "indigo").set(5)
        assert (
            get_metric_from_frozen_registry(
                "some_labelled_gauge",
                frozen_registry,
                labelred="pink",
                labelblue="indigo",
            )
            == 1
        )
        assert_metric_diff(
            frozen_registry,
            5 - 1,
            "some_labelled_gauge",
            registry=registry,
            labelred="pink",
            labelblue="indigo",
        )

        assert_metric_no_diff(
            frozen_registry,
            1,
            "some_labelled_gauge",
            registry=registry,
            labelred="pink",
            labelblue="indigo",
        )
