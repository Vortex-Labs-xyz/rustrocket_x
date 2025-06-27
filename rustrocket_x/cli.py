"""Main CLI application for rustrocket_x"""

import os

import typer
from rich.console import Console

from . import __version__
from .commands import autopost, metrics
from .metrics import DURATION, FAILURES, RUNS, init_metrics

console = Console()
app = typer.Typer(
    name="rrx",
    help="rustrocket_x - X/Twitter API analytics (Free Plan)",
    add_completion=False,
)

# Initialize Prometheus metrics exporter (only in production)
if os.getenv("PYTEST_CURRENT_TEST") is None:  # Skip in tests
    init_metrics()  # exporter up on port 9100

# Add subcommands
app.add_typer(metrics.app, name="metrics", help="X/Twitter metrics and analytics")
app.add_typer(autopost.app, name="autopost", help="X/Twitter automation and posting")


def version_callback(value: bool):
    if value:
        console.print(f"rustrocket_x version: {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, help="Show version and exit"
    ),
):
    """rustrocket_x - X/Twitter API analytics tool"""
    if ctx.invoked_subcommand is None:
        return

    with DURATION.time():
        RUNS.inc()
        try:
            # Command execution is handled by typer automatically
            pass
        except Exception:
            FAILURES.inc()
            raise


if __name__ == "__main__":
    app()
