from django.core.cache.backends import filebased

from django_prometheus.cache.metrics import (
    django_cache_get_total,
    django_cache_hits_total,
    django_cache_misses_total,
)


class FileBasedCache(filebased.FileBasedCache):
    """Inherit filebased cache to add metrics about hit/miss ratio"""

    def get(self, key, default=None, version=None):
        django_cache_get_total.labels(backend="filebased").inc()
        cached = super().get(key, default=None, version=version)
        if cached is not None:
            django_cache_hits_total.labels(backend="filebased").inc()
            return cached

        django_cache_misses_total.labels(backend="filebased").inc()
        return default
