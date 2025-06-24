"""Main CLI application for rustrocket_x"""

import typer
from rich.console import Console

from . import __version__
from .commands import autopost, metrics

console = Console()
app = typer.Typer(
    name="rrx",
    help="rustrocket_x - X/Twitter API analytics (Free Plan)",
    add_completion=False,
)

# Add subcommands
app.add_typer(metrics.app, name="metrics", help="X/Twitter metrics and analytics")
app.add_typer(autopost.app, name="autopost", help="X/Twitter automation and posting")


def version_callback(value: bool):
    if value:
        console.print(f"rustrocket_x version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, help="Show version and exit"
    ),
):
    """rustrocket_x - X/Twitter API analytics tool"""
    pass


if __name__ == "__main__":
    app()
