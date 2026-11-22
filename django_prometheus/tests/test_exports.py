#!/usr/bin/env python
import logging
import socket
from unittest.mock import ANY, MagicMock, call, patch

from django_prometheus.exports import MetricsHTTPServer, SetupPrometheusEndpointOnPortRange


@patch("django_prometheus.exports.MetricsHTTPServer")
def test_port_range_available(httpserver_mock):
    """Test port range setup with an available port."""
    httpserver_mock.side_effect = [socket.error, MagicMock()]
    port_range = [8000, 8001]
    port_chosen = SetupPrometheusEndpointOnPortRange(port_range)
    assert port_chosen in port_range

    expected_calls = [call(("", 8000), ANY), call(("", 8001), ANY)]
    assert httpserver_mock.mock_calls == expected_calls


@patch("django_prometheus.exports.MetricsHTTPServer")
def test_port_range_unavailable(httpserver_mock):
    """Test port range setup with no available ports."""
    httpserver_mock.side_effect = [socket.error, socket.error]
    port_range = [8000, 8001]
    port_chosen = SetupPrometheusEndpointOnPortRange(port_range)

    expected_calls = [call(("", 8000), ANY), call(("", 8001), ANY)]
    assert httpserver_mock.mock_calls == expected_calls
    assert port_chosen is None


def test_handler_errors_are_logged(caplog):
    """Errors raised while serving a scrape go to logging, not stderr."""
    server = MetricsHTTPServer(("127.0.0.1", 0), MagicMock())
    try:
        with caplog.at_level(logging.ERROR, logger="django_prometheus.exports"):
            try:
                raise BrokenPipeError("client went away")
            except BrokenPipeError:
                server.handle_error(MagicMock(), ("127.0.0.1", 12345))
    finally:
        server.server_close()

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "Exception while serving Prometheus metrics" in record.getMessage()
    assert record.exc_info[0] is BrokenPipeError
