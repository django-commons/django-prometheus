from django.core.cache.backends import memcached

from django_prometheus.cache.metrics import (
    django_cache_get_total,
    django_cache_hits_total,
    django_cache_misses_total,
)


class MemcachedPrometheusCacheMixin:
    def get(self, key, default=None, version=None):
        django_cache_get_total.labels(backend="memcached").inc()
        cached = super().get(key, default=None, version=version)
        if cached is not None:
            django_cache_hits_total.labels(backend="memcached").inc()
            return cached

        django_cache_misses_total.labels(backend="memcached").inc()
        return default


class PyLibMCCache(MemcachedPrometheusCacheMixin, memcached.PyLibMCCache):
    """Inherit memcached to add metrics about hit/miss ratio"""


class PyMemcacheCache(MemcachedPrometheusCacheMixin, memcached.PyMemcacheCache):
    """Inherit memcached to add metrics about hit/miss ratio"""
