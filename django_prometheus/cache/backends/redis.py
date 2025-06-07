import warnings

from django.core.cache.backends.redis import RedisCache as DjangoRedisCache

from django_prometheus.cache.metrics import (
    django_cache_get_fail_total,
    django_cache_get_total,
    django_cache_hits_total,
    django_cache_misses_total,
)


class RedisCache(DjangoRedisCache):
    def get(self, key, default=None, version=None):
        django_cache_get_total.labels(backend="redis").inc()
        try:
            result = super().get(key, default=None, version=version)
        except Exception:
            django_cache_get_fail_total.labels(backend="redis").inc()
            raise
        if result is not None:
            django_cache_hits_total.labels(backend="redis").inc()
            return result
        django_cache_misses_total.labels(backend="native_redis").inc()
        return default


class NativeRedisCache(RedisCache):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "NativeRedisCache is renamed, use RedisCache instead",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
