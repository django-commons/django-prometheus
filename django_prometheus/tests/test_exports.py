#!/usr/bin/env python
import socket
from unittest.mock import ANY, MagicMock, call, patch

from prometheus_client import REGISTRY

from django_prometheus.exports import SetupPrometheusEndpointOnPortRange


@patch("django_prometheus.exports.HTTPServer")
def test_port_range_available(httpserver_mock):
    """Test port range setup with an available port."""
    httpserver_mock.side_effect = [socket.error, MagicMock()]
    port_range = [8000, 8001]
    port_chosen = SetupPrometheusEndpointOnPortRange(REGISTRY, port_range)
    assert port_chosen in port_range

    expected_calls = [call(("", 8000), ANY), call(("", 8001), ANY)]
    assert httpserver_mock.mock_calls == expected_calls


@patch("django_prometheus.exports.HTTPServer")
def test_port_range_unavailable(httpserver_mock):
    """Test port range setup with no available ports."""
    httpserver_mock.side_effect = [socket.error, socket.error]
    port_range = [8000, 8001]
    port_chosen = SetupPrometheusEndpointOnPortRange(REGISTRY, port_range)

    expected_calls = [call(("", 8000), ANY), call(("", 8001), ANY)]
    assert httpserver_mock.mock_calls == expected_calls
    assert port_chosen is None
