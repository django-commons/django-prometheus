"""Django-Prometheus

https://github.com/korfuri/django-prometheus
"""

# Import all files that define metrics. This has the effect that
# `import django_prometheus` will always instantiate all metric
# objects right away.
from django_prometheus import middleware, models

__all__ = ["middleware", "models", "pip_prometheus"]

__version__ = "2.4.1"

# Import pip_prometheus to export the pip metrics automatically.
try:
    import pip_prometheus
except ImportError:
    # If people don't have pip, don't export anything.
    pass
