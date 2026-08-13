#!/usr/bin/env python
import time

from django_prometheus.utils import PowersOf, Time, TimeSince


def test_time_value_is_usable_with_timesince():
    """Time() returns an opaque value TimeSince() turns into fractional seconds."""
    elapsed = TimeSince(Time())
    assert isinstance(elapsed, float)
    assert elapsed >= 0


def test_time_is_monotonic_nondecreasing():
    """Successive calls to Time() never go backwards."""
    t1 = Time()
    t2 = Time()
    assert t2 >= t1


def test_timesince_is_nonnegative_and_small_for_immediate_call():
    """TimeSince() of a just-captured Time() is a small, non-negative value."""
    t = Time()
    elapsed = TimeSince(t)
    assert elapsed >= 0
    assert elapsed < 1.0


def test_timesince_measures_elapsed_time():
    """TimeSince() reflects the time that actually elapsed between the two calls."""
    t = Time()
    time.sleep(0.02)
    assert TimeSince(t) >= 0.02


def test_powersof_includes_zero_by_default():
    """PowersOf() prepends 0 and returns count powers of logbase."""
    assert PowersOf(2, 4) == [0, 1, 2, 4, 8]


def test_powersof_without_zero():
    """include_zero=False drops the leading 0."""
    assert PowersOf(2, 4, include_zero=False) == [1, 2, 4, 8]


def test_powersof_with_lower_bound():
    """lower shifts the starting exponent."""
    assert PowersOf(10, 3, lower=1, include_zero=False) == [10, 100, 1000]
    assert PowersOf(10, 3, lower=1) == [0, 10, 100, 1000]
