#!/usr/bin/env python
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, call, patch

import prometheus_client
import pytest

from django_prometheus.exports import (
    ExportToDjangoView,
    PrometheusEndpointServer,
    SetupPrometheusEndpointOnPort,
    SetupPrometheusEndpointOnPortRange,
    SetupPrometheusExportsFromConfig,
)


@patch("django_prometheus.exports.HTTPServer")
def test_port_range_available(httpserver_mock):
    """Test port range setup with an available port."""
    httpserver_mock.side_effect = [OSError, MagicMock()]
    port_range = [8000, 8001]
    port_chosen = SetupPrometheusEndpointOnPortRange(port_range)
    assert port_chosen in port_range

    expected_calls = [call(("", 8000), ANY), call(("", 8001), ANY)]
    assert httpserver_mock.mock_calls == expected_calls


@patch("django_prometheus.exports.HTTPServer")
def test_port_range_unavailable(httpserver_mock):
    """Test port range setup with no available ports."""
    httpserver_mock.side_effect = [OSError, OSError]
    port_range = [8000, 8001]
    port_chosen = SetupPrometheusEndpointOnPortRange(port_range)

    expected_calls = [call(("", 8000), ANY), call(("", 8001), ANY)]
    assert httpserver_mock.mock_calls == expected_calls
    assert port_chosen is None


@patch("django_prometheus.exports.prometheus_client.start_http_server")
def test_setup_on_port_starts_http_server(start_http_server):
    SetupPrometheusEndpointOnPort(9100, addr="127.0.0.1")
    start_http_server.assert_called_once_with(9100, addr="127.0.0.1")


def test_setup_on_port_rejects_django_autoreloader(monkeypatch):
    monkeypatch.setenv("RUN_MAIN", "true")
    with pytest.raises(AssertionError, match="autoreloader"):
        SetupPrometheusEndpointOnPort(9100)


def test_setup_on_port_range_rejects_django_autoreloader(monkeypatch):
    monkeypatch.setenv("RUN_MAIN", "true")
    with pytest.raises(AssertionError, match="autoreloader"):
        SetupPrometheusEndpointOnPortRange([8000])


def test_prometheus_endpoint_server_serves_forever():
    httpd = MagicMock()
    server = PrometheusEndpointServer(httpd)
    server.run()
    httpd.serve_forever.assert_called_once_with()


@patch("django_prometheus.exports.SetupPrometheusEndpointOnPortRange")
@patch("django_prometheus.exports.SetupPrometheusEndpointOnPort")
def test_config_prefers_port_range(setup_on_port, setup_on_port_range):
    settings = SimpleNamespace(
        PROMETHEUS_METRICS_EXPORT_PORT=8001,
        PROMETHEUS_METRICS_EXPORT_PORT_RANGE=range(8001, 8003),
        PROMETHEUS_METRICS_EXPORT_ADDRESS="127.0.0.1",
    )
    with patch("django_prometheus.exports.settings", settings):
        SetupPrometheusExportsFromConfig()

    setup_on_port_range.assert_called_once_with(range(8001, 8003), "127.0.0.1")
    setup_on_port.assert_not_called()


@patch("django_prometheus.exports.SetupPrometheusEndpointOnPortRange")
@patch("django_prometheus.exports.SetupPrometheusEndpointOnPort")
def test_config_uses_single_port(setup_on_port, setup_on_port_range):
    settings = SimpleNamespace(
        PROMETHEUS_METRICS_EXPORT_PORT=8001,
        PROMETHEUS_METRICS_EXPORT_ADDRESS="",
    )
    with patch("django_prometheus.exports.settings", settings):
        SetupPrometheusExportsFromConfig()

    setup_on_port.assert_called_once_with(8001, "")
    setup_on_port_range.assert_not_called()


@patch("django_prometheus.exports.SetupPrometheusEndpointOnPortRange")
@patch("django_prometheus.exports.SetupPrometheusEndpointOnPort")
def test_config_is_noop_without_port_settings(setup_on_port, setup_on_port_range):
    with patch("django_prometheus.exports.settings", SimpleNamespace()):
        SetupPrometheusExportsFromConfig()

    setup_on_port.assert_not_called()
    setup_on_port_range.assert_not_called()


def test_export_to_django_view_uses_default_registry():
    response = ExportToDjangoView(MagicMock())

    assert response.status_code == 200
    assert response["Content-Type"] == prometheus_client.CONTENT_TYPE_LATEST
    assert response.content  # Prometheus exposition format is non-empty


@patch("django_prometheus.exports.multiprocess.MultiProcessCollector")
@patch("django_prometheus.exports.prometheus_client.generate_latest", return_value=b"# multiproc\n")
def test_export_to_django_view_uses_multiprocess_registry(generate_latest, multiproc_collector, monkeypatch):
    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus-multiproc")

    response = ExportToDjangoView(MagicMock())

    multiproc_collector.assert_called_once()
    generate_latest.assert_called_once()
    assert response.content == b"# multiproc\n"
    assert response["Content-Type"] == prometheus_client.CONTENT_TYPE_LATEST


@patch("django_prometheus.exports.multiprocess.MultiProcessCollector")
@patch("django_prometheus.exports.prometheus_client.generate_latest", return_value=b"# multiproc-legacy\n")
def test_export_to_django_view_accepts_legacy_multiproc_env(_generate_latest, multiproc_collector, monkeypatch):
    monkeypatch.setenv("prometheus_multiproc_dir", "/tmp/prometheus-multiproc-legacy")

    response = ExportToDjangoView(MagicMock())

    multiproc_collector.assert_called_once()
    assert response.content == b"# multiproc-legacy\n"
