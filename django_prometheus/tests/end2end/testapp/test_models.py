import pytest

from django_prometheus.testutils import assert_metric_diff, save_registry
from testapp.models import Dog, Lawn


def M(metric_name):
    """Make a full metric name from a short metric name.

    This is just intended to help keep the lines shorter in test
    cases.
    """
    return f"django_model_{metric_name}"


@pytest.mark.django_db
class TestModelMetrics:
    """Test django_prometheus.models."""

    def test_counters(self):
        registry = save_registry()
        cool = Dog()
        cool.name = "Cool"
        cool.save()
        assert_metric_diff(registry, 1, M("inserts_total"), model="dog")

        elysees = Lawn()
        elysees.location = "Champs Elysees, Paris"
        elysees.save()
        assert_metric_diff(registry, 1, M("inserts_total"), model="lawn")
        assert_metric_diff(registry, 1, M("inserts_total"), model="dog")

        galli = Dog()
        galli.name = "Galli"
        galli.save()
        assert_metric_diff(registry, 2, M("inserts_total"), model="dog")

        cool.breed = "Wolfhound"
        assert_metric_diff(registry, 2, M("inserts_total"), model="dog")

        cool.save()
        assert_metric_diff(registry, 2, M("inserts_total"), model="dog")
        assert_metric_diff(registry, 1, M("updates_total"), model="dog")

        cool.age = 9
        cool.save()
        assert_metric_diff(registry, 2, M("updates_total"), model="dog")

        cool.delete()  # :(
        assert_metric_diff(registry, 2, M("inserts_total"), model="dog")
        assert_metric_diff(registry, 2, M("updates_total"), model="dog")
        assert_metric_diff(registry, 1, M("deletes_total"), model="dog")
