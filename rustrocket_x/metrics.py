"""
Prometheus metrics exporter for rustrocket_x CLI

Exposes CLI usage metrics on port 9100 for monitoring and observability.
"""

from prometheus_client import Counter, Histogram, start_http_server

# Metrics definitions
RUNS = Counter("rrx_runs_total", "Total CLI runs")
FAILURES = Counter("rrx_failures_total", "Runs that raised an exception") 
DURATION = Histogram("rrx_duration_seconds", "Execution time")

def init_metrics(port: int = 9100):
    """
    Initialize Prometheus metrics HTTP server
    
    Args:
        port: Port to serve metrics on (default: 9100)
    """
    start_http_server(port)  # non-blocking 