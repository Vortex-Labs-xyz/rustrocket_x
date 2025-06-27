"""
Prometheus metrics exporter for rustrocket_x CLI

Exposes CLI usage metrics on port 9100 for monitoring and observability.
"""

import os

from prometheus_client import Counter, Histogram, start_http_server

# Metrics definitions
RUNS = Counter("rrx_runs_total", "Total CLI runs")
FAILURES = Counter("rrx_failures_total", "Runs that raised an exception")
DURATION = Histogram("rrx_duration_seconds", "Execution time")

_metrics_server_started = False


def init_metrics(port: int = 9100):
    """
    Initialize Prometheus metrics HTTP server

    Args:
        port: Port to serve metrics on (default: 9100)
    """
    global _metrics_server_started

    # Skip in test environment
    if os.getenv("PYTEST_CURRENT_TEST"):
        return

    # Only start once
    if _metrics_server_started:
        return

    try:
        start_http_server(port)  # non-blocking
        _metrics_server_started = True
    except OSError:
        # Port already in use, silently continue
        pass
