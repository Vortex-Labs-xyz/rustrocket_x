"""Metrics commands for X/Twitter analytics"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..utils.x_api import XAPIClient

console = Console()
app = typer.Typer(name="metrics", help="X/Twitter metrics and analytics commands")


@app.command("pull")
def pull_metrics(
    user: str = typer.Option(..., "--user", "-u", help="Twitter username (without @)"),
    outfile: Optional[str] = typer.Option(
        None,
        "--outfile",
        "-o",
        help="Output file path (default: data/x_metrics_<date>.json)",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview only, don't write to file"
    ),
):
    """Pull user metrics from X/Twitter API"""

    # Initialize API client
    client = XAPIClient()

    try:
        # Fetch user metrics
        with console.status(f"[bold green]Fetching metrics for @{user}..."):
            response = client.get_user_metrics(user)

        if "data" not in response:
            console.print(
                f"[red]Error: User @{user} not found or no data available[/red]"
            )
            raise typer.Exit(1)

        user_data = response["data"]
        public_metrics = user_data.get("public_metrics", {})

        # Create metrics data
        metrics_data = {
            "username": user,
            "user_id": user_data.get("id"),
            "name": user_data.get("name"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "followers_count": public_metrics.get("followers_count", 0),
                "following_count": public_metrics.get("following_count", 0),
                "tweet_count": public_metrics.get("tweet_count", 0),
                "listed_count": public_metrics.get("listed_count", 0),
                "like_count": public_metrics.get("like_count", 0),
            },
        }

        # Display metrics in a nice table
        _display_metrics(user, metrics_data["metrics"])

        if dry_run:
            console.print("\n[yellow]Dry-run: no file written[/yellow]")
            return

        # Generate output filename if not provided
        if not outfile:
            date_str = datetime.now().strftime("%Y%m%d")
            outfile = f"data/x_metrics_{date_str}.json"

        # Ensure directory exists
        output_path = Path(outfile)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)

        console.print(f"\n[green]✅ Metrics saved to: {outfile}[/green]")

    except Exception as e:
        console.print(f"[red]Error fetching metrics: {e}[/red]")
        raise typer.Exit(1) from e


def _display_metrics(username: str, metrics: dict):
    """Display metrics in a formatted table"""

    table = Table(title=f"X/Twitter Metrics for @{username}")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", style="magenta", justify="right")

    table.add_row("Followers", f"{metrics.get('followers_count', 0):,}")
    table.add_row("Following", f"{metrics.get('following_count', 0):,}")
    table.add_row("Tweets", f"{metrics.get('tweet_count', 0):,}")
    table.add_row("Listed", f"{metrics.get('listed_count', 0):,}")
    table.add_row("Likes", f"{metrics.get('like_count', 0):,}")

    console.print()
    console.print(table)
    console.print()
