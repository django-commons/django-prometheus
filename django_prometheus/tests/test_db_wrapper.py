"""Tests for the PostgreSQL and PostGIS database backend wrappers.

Verifies that cursor_factory wrapping works correctly and does not
re-wrap when connections are reused from a pool (issue #445).
"""

from unittest.mock import MagicMock, patch

import pytest

from django_prometheus.db.common import ExportingCursorWrapper

try:
    from django.contrib.gis.gdal import libgdal  # noqa: F401

    _has_gdal = True
except Exception:
    _has_gdal = False

import os

_can_import_postgis_backend = False
if os.environ.get("DJANGO_SETTINGS_MODULE"):
    try:
        import django.contrib.gis.db.backends.postgis.base  # noqa: F401

        _can_import_postgis_backend = True
    except Exception:
        pass


class DummyCursor:
    """A stand-in cursor class used as the base cursor_factory."""

    def execute(self, *args, **kwargs):
        pass

    def executemany(self, query, param_list, *args, **kwargs):
        pass


class TestExportingCursorWrapper:
    def test_wraps_cursor_class(self):
        """ExportingCursorWrapper returns a subclass of the given cursor class."""
        wrapped = ExportingCursorWrapper(DummyCursor, "default", "postgresql")
        assert issubclass(wrapped, DummyCursor)

    def test_double_wrapping_increases_mro(self):
        """Wrapping an already-wrapped class creates deeper inheritance.

        This is the root cause of #445: each re-wrap adds a layer to the
        MRO, so execute() traverses more super() calls over time.
        """
        wrapped_once = ExportingCursorWrapper(DummyCursor, "default", "postgresql")
        wrapped_twice = ExportingCursorWrapper(wrapped_once, "default", "postgresql")
        assert len(wrapped_twice.__mro__) > len(wrapped_once.__mro__)


class TestPostgresqlGetConnectionParams:
    """Test that the postgresql backend wraps cursor_factory in get_connection_params."""

    def _make_wrapper(self):
        """Create a DatabaseWrapper instance with mocked internals."""
        from django_prometheus.db.backends.postgresql import base as pg_base

        wrapper = pg_base.DatabaseWrapper.__new__(pg_base.DatabaseWrapper)
        wrapper.alias = "default"
        wrapper.vendor = "postgresql"
        return wrapper

    @patch("django.db.backends.postgresql.base.DatabaseWrapper.get_connection_params")
    def test_wraps_cursor_factory(self, mock_super_params):
        mock_super_params.return_value = {"cursor_factory": DummyCursor}
        wrapper = self._make_wrapper()

        params = wrapper.get_connection_params()

        assert params["cursor_factory"] is not DummyCursor
        assert issubclass(params["cursor_factory"], DummyCursor)

    @patch("django.db.backends.postgresql.base.DatabaseWrapper.get_connection_params")
    def test_wrapping_is_single_layer(self, mock_super_params):
        """Calling get_connection_params() always wraps the base cursor class,
        not a previously wrapped one, because super() returns the original params.

        With connection pooling, get_connection_params() is called once at pool
        creation, so the cursor_factory is wrapped exactly once per pool.
        """
        mock_super_params.side_effect = lambda: {"cursor_factory": DummyCursor}
        wrapper = self._make_wrapper()

        params_first = wrapper.get_connection_params()
        params_second = wrapper.get_connection_params()

        # Both calls produce the same MRO depth because super() always
        # returns the unwrapped DummyCursor as the base.
        assert len(params_first["cursor_factory"].__mro__) == len(params_second["cursor_factory"].__mro__)

    @patch("django.db.backends.postgresql.base.DatabaseWrapper.get_new_connection")
    def test_get_new_connection_does_not_rewrap(self, mock_super_conn):
        """get_new_connection() no longer modifies cursor_factory on the
        connection, so pooled connections are not re-wrapped.
        """

        mock_conn = MagicMock()
        already_wrapped = ExportingCursorWrapper(DummyCursor, "default", "postgresql")
        mock_conn.cursor_factory = already_wrapped
        mock_super_conn.return_value = mock_conn

        wrapper = self._make_wrapper()
        conn = wrapper.get_new_connection({})

        # cursor_factory should be untouched — still the same class
        assert conn.cursor_factory is already_wrapped

    @patch("django.db.backends.postgresql.base.DatabaseWrapper.create_cursor")
    def test_create_cursor_delegates_to_django(self, mock_django_create_cursor):
        """create_cursor() delegates to Django's base implementation,
        not the mixin's version which is incompatible with psycopg3.
        """
        mock_django_create_cursor.return_value = MagicMock()
        wrapper = self._make_wrapper()

        wrapper.create_cursor(name=None)

        # Called as an unbound method: base.DatabaseWrapper.create_cursor(self, name=None)
        mock_django_create_cursor.assert_called_once_with(wrapper, name=None)


@pytest.mark.skipif(
    not _has_gdal or not _can_import_postgis_backend,
    reason="PostGIS tests require GDAL and a fully configured Django environment",
)
class TestPostgisGetConnectionParams:
    """Test that the postgis backend wraps cursor_factory in get_connection_params."""

    def _get_django_postgis_dbwrapper(self):
        """Return the Django PostGIS DatabaseWrapper class for patch.object()."""
        from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper

        return DatabaseWrapper

    def _make_wrapper(self):
        """Create a PostGIS DatabaseWrapper instance with mocked internals."""
        from django_prometheus.db.backends.postgis import base as gis_base

        wrapper = gis_base.DatabaseWrapper.__new__(gis_base.DatabaseWrapper)
        wrapper.alias = "geo_db"
        wrapper.vendor = "postgresql"
        return wrapper

    def test_wraps_cursor_factory(self):
        with patch.object(self._get_django_postgis_dbwrapper(), "get_connection_params") as mock_super_params:
            mock_super_params.return_value = {"cursor_factory": DummyCursor}
            wrapper = self._make_wrapper()

            params = wrapper.get_connection_params()

            assert params["cursor_factory"] is not DummyCursor
            assert issubclass(params["cursor_factory"], DummyCursor)

    def test_wrapping_is_single_layer(self):
        """Each call wraps the original cursor class, not a previously wrapped one."""
        with patch.object(self._get_django_postgis_dbwrapper(), "get_connection_params") as mock_super_params:
            mock_super_params.side_effect = lambda: {"cursor_factory": DummyCursor}
            wrapper = self._make_wrapper()

            params_first = wrapper.get_connection_params()
            params_second = wrapper.get_connection_params()

            assert len(params_first["cursor_factory"].__mro__) == len(params_second["cursor_factory"].__mro__)

    def test_uses_self_alias(self):
        """The postgis backend uses self.alias, not a hardcoded string."""
        with patch.object(self._get_django_postgis_dbwrapper(), "get_connection_params") as mock_super_params:
            mock_super_params.return_value = {"cursor_factory": DummyCursor}
            wrapper = self._make_wrapper()

            with patch("django_prometheus.db.common.ExportingCursorWrapper") as mock_ecw:
                mock_ecw.return_value = DummyCursor
                wrapper.get_connection_params()
                mock_ecw.assert_called_once_with(DummyCursor, "geo_db", "postgresql")

    def test_create_cursor_delegates_to_django(self):
        """create_cursor() delegates to Django's postgis base implementation."""
        with patch.object(self._get_django_postgis_dbwrapper(), "create_cursor") as mock_django_create_cursor:
            mock_django_create_cursor.return_value = MagicMock()
            wrapper = self._make_wrapper()

            wrapper.create_cursor(name=None)

            mock_django_create_cursor.assert_called_once_with(wrapper, name=None)
