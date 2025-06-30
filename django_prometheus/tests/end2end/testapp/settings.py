import os
import tempfile

from testapp.helpers import get_middleware

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ")0-t%mc5y1^fn8e7i**^^v166@5iu(&-2%9#kxud0&4ap#k!_k"
DEBUG = True
ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_prometheus",
    "testapp",
)


MIDDLEWARE = get_middleware(
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
)

ROOT_URLCONF = "testapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "testapp.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    },
    # Comment this to not test django_prometheus.db.backends.postgres.
    "postgresql": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "5432",
    },
    # Comment this to not test django_prometheus.db.backends.postgis.
    "postgis": {
        "ENGINE": "django_prometheus.db.backends.postgis",
        "NAME": "postgis",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "5432",
    },
    # Comment this to not test django_prometheus.db.backends.mysql.
    "mysql": {
        "ENGINE": "django_prometheus.db.backends.mysql",
        "NAME": "django_prometheus_1",
        "USER": "root",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    },
    "spatialite": {
        "ENGINE": "django_prometheus.db.backends.spatialite",
        "NAME": "db_spatialite.sqlite3",
    },
    # The following databases are used by test_db.py only
    "test_db_1": {
        "ENGINE": "django_prometheus.db.backends.sqlite3",
        "NAME": "test_db_1.sqlite3",
    },
    "test_db_2": {
        "ENGINE": "django_prometheus.db.backends.sqlite3",
        "NAME": "test_db_2.sqlite3",
    },
}

# Caches
_tmp_cache_dir = tempfile.mkdtemp()

CACHES = {
    "default": {
        "BACKEND": "django_prometheus.cache.backends.memcached.PyLibMCCache",
        "LOCATION": "localhost:11211",
    },
    "memcached.PyLibMCCache": {
        "BACKEND": "django_prometheus.cache.backends.memcached.PyLibMCCache",
        "LOCATION": "localhost:11211",
    },
    "memcached.PyMemcacheCache": {
        "BACKEND": "django_prometheus.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "localhost:11211",
    },
    "filebased": {
        "BACKEND": "django_prometheus.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(_tmp_cache_dir, "django_cache"),
    },
    "locmem": {
        "BACKEND": "django_prometheus.cache.backends.locmem.LocMemCache",
        "LOCATION": os.path.join(_tmp_cache_dir, "locmem_cache"),
    },
    "redis": {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    },
    # Fake redis config emulated stopped service
    "stopped_redis": {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6666/1",
    },
    "stopped_redis_ignore_exception": {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6666/1",
        "OPTIONS": {"IGNORE_EXCEPTIONS": True},
    },
}


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {"django": {"handlers": ["console"], "level": "INFO"}},
}
