#!/usr/bin/env python
from django_prometheus.utils import PowersOf


class TestDjangoPrometheus:
    def testPowersOf(self):
        """Tests utils.PowersOf."""
        assert PowersOf(2, 4) == [0, 1, 2, 4, 8]
        assert PowersOf(3, 5, lower=1) == [0, 3, 9, 27, 81, 243]
        assert PowersOf(2, 4, include_zero=False) == [1, 2, 4, 8]
        assert PowersOf(2, 6, lower=2, include_zero=False) == [4, 8, 16, 32, 64, 128]
