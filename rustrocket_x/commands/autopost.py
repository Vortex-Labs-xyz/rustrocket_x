"""
Autopost command for X/Twitter automation

Content Pipeline:
1. Scan queue directory for .tweet.md/.tweet.txt files
2. Parse YAML front-matter (pin:true, reply_to:<id>)
3. Convert Markdown to plain text (max 280 chars)
4. Post via OAuth 1.0a (Basic Plan: 300 tweets/3h)
5. Move to done/ directory + JSON log
6. Pin tweets if requested

Rate Limits: Built-in 1s sleep + exponential backoff on 429
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import frontmatter
import markdown
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..utils.twitter import get_twitter_client

console = Console()
app = typer.Typer(name="autopost", help="X/Twitter automation commands")


def markdown_to_text(content: str) -> str:
    """
    Convert Markdown to plain text for tweets

    Args:
        content: Markdown content

    Returns:
        Plain text suitable for Twitter
    """
    # Convert markdown to HTML, then strip HTML tags
    html = markdown.markdown(content, extensions=["markdown.extensions.codehilite"])

    # Simple HTML tag removal (basic approach)
    import re

    text = re.sub(r"<[^>]+>", "", html)

    # Clean up extra whitespace
    text = " ".join(text.split())

    return text.strip()


def validate_tweet_length(text: str, max_length: int = 280) -> bool:
    """
    Validate tweet length

    Args:
        text: Tweet text
        max_length: Maximum allowed length

    Returns:
        True if valid length
    """
    return len(text) <= max_length


def load_pinned_tweets(pin_file: Path) -> List[str]:
    """
    Load list of pinned tweet IDs from file

    Args:
        pin_file: Path to pinned tweets file

    Returns:
        List of tweet IDs
    """
    if not pin_file.exists():
        return []

    try:
        with open(pin_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load pinned tweets: {e}[/yellow]")
        return []


def save_pinned_tweet(pin_file: Path, tweet_id: str) -> None:
    """
    Save tweet ID to pinned tweets file

    Args:
        pin_file: Path to pinned tweets file
        tweet_id: Tweet ID to save
    """
    try:
        with open(pin_file, "a", encoding="utf-8") as f:
            f.write(f"{tweet_id}\n")
    except Exception as e:
        console.print(f"[red]Error saving pinned tweet: {e}[/red]")


def log_tweet_result(
    log_file: Path,
    filename: str,
    tweet_id: str,
    text: str,
    metadata: Dict[str, Any],
    success: bool = True,
    error: Optional[str] = None,
) -> None:
    """
    Log tweet posting result as JSON line

    Args:
        log_file: Path to log file
        filename: Original filename
        tweet_id: Posted tweet ID
        text: Tweet text
        metadata: Front-matter metadata
        success: Whether posting was successful
        error: Error message if failed
    """
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "filename": filename,
        "tweet_id": tweet_id,
        "text": text,
        "metadata": metadata,
        "success": success,
        "error": error,
        "char_count": len(text),
    }

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        console.print(f"[red]Error writing log: {e}[/red]")


def process_tweet_file(
    file_path: Path, twitter_client, dry_run: bool = False
) -> Dict[str, Any]:
    """
    Process a single tweet file

    Args:
        file_path: Path to tweet file
        twitter_client: Twitter client instance
        dry_run: Whether to run in dry-run mode

    Returns:
        Processing result dictionary
    """
    try:
        # Load and parse file with front-matter
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # Extract metadata and content
        metadata = post.metadata
        content = post.content.strip()

        # Convert markdown to text if needed
        if file_path.suffix == ".md":
            text = markdown_to_text(content)
        else:
            text = content

        # Validate length
        if not validate_tweet_length(text):
            return {
                "success": False,
                "error": f"Tweet too long: {len(text)} characters (max 280)",
                "text": text,
                "metadata": metadata,
            }

        # Get reply_to from metadata
        reply_to = metadata.get("reply_to")

        # Post tweet
        tweet_id = twitter_client.post_tweet(text, reply_to=reply_to)

        # Pin if requested
        should_pin = metadata.get("pin", False)
        if should_pin and not dry_run:
            twitter_client.pin_tweet(tweet_id)
        elif should_pin and dry_run:
            console.print("[cyan]DRY-RUN: Would pin tweet[/cyan]")

        return {
            "success": True,
            "tweet_id": tweet_id,
            "text": text,
            "metadata": metadata,
            "pinned": should_pin,
        }

    except Exception as e:
        return {"success": False, "error": str(e), "text": "", "metadata": {}}


def setup_directories(queue_dir: str, done_dir: str) -> tuple[Path, Path, Path]:
    """Setup and create necessary directories"""
    queue_path = Path(queue_dir)
    done_path = Path(done_dir)
    log_file = done_path / "autopost.log"

    queue_path.mkdir(parents=True, exist_ok=True)
    done_path.mkdir(parents=True, exist_ok=True)

    return queue_path, done_path, log_file


def discover_tweet_files(queue_path: Path, max_tweets: int) -> List[Path]:
    """Discover and sort tweet files from queue directory"""
    tweet_files = []
    for pattern in ["*.tweet.md", "*.tweet.txt"]:
        tweet_files.extend(queue_path.glob(pattern))

    # Sort by modification time (oldest first)
    tweet_files.sort(key=lambda f: f.stat().st_mtime)

    # Limit number of tweets
    return tweet_files[:max_tweets]


def display_queue_status(tweet_files: List[Path], dry_run: bool) -> None:
    """Display the current queue status"""
    console.print(f"\n[cyan]Found {len(tweet_files)} tweet file(s) to process:[/cyan]")

    # Display files to process
    table = Table(title="Tweet Queue")
    table.add_column("File", style="cyan")
    table.add_column("Size", style="dim")
    table.add_column("Modified", style="dim")

    for file_path in tweet_files:
        size = file_path.stat().st_size
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        table.add_row(file_path.name, f"{size} bytes", mtime.strftime("%Y-%m-%d %H:%M"))

    console.print(table)

    if dry_run:
        console.print("\n[yellow]DRY-RUN MODE: No actual posting will occur[/yellow]")


def process_all_tweets(
    tweet_files: List[Path],
    twitter_client,
    dry_run: bool,
    log_file: Path,
    pin_file_path: Path,
    done_path: Path
) -> tuple[int, int]:
    """Process all tweet files and return success/error counts"""
    success_count = 0
    error_count = 0

    for file_path in tweet_files:
        console.print(f"\n[bold]Processing: {file_path.name}[/bold]")

        try:
            # Process the tweet
            result = process_tweet_file(file_path, twitter_client, dry_run)

            if result["success"]:
                tweet_id = result["tweet_id"]
                text = result["text"]
                metadata = result["metadata"]

                console.print(f"[green]✅ Success: {tweet_id}[/green]")
                console.print(
                    f"[dim]Text: {text[:100]}{'...' if len(text) > 100 else ''}[/dim]"
                )

                # Log the result
                if not dry_run:
                    log_tweet_result(log_file, file_path.name, tweet_id, text, metadata)

                    # Save pinned tweet ID
                    if result.get("pinned", False):
                        save_pinned_tweet(pin_file_path, tweet_id)

                    # Move file to done directory
                    done_file = done_path / file_path.name
                    shutil.move(str(file_path), str(done_file))
                    console.print(f"[dim]Moved to: {done_file}[/dim]")

                success_count += 1

            else:
                console.print(f"[red]❌ Error: {result['error']}[/red]")

                # Log the error
                if not dry_run:
                    log_tweet_result(
                        log_file,
                        file_path.name,
                        "",
                        result.get("text", ""),
                        result.get("metadata", {}),
                        success=False,
                        error=result["error"],
                    )

                error_count += 1

        except Exception as e:
            console.print(
                f"[red]❌ Unexpected error processing {file_path.name}: {e}[/red]"
            )
            error_count += 1

    return success_count, error_count


def display_summary(
    success_count: int, error_count: int, dry_run: bool, log_file: Path
) -> None:
    """Display processing summary"""
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"✅ Successful: {success_count}")
    console.print(f"❌ Errors: {error_count}")

    if not dry_run and success_count > 0:
        console.print(f"📝 Log written to: {log_file}")

    if dry_run:
        console.print("[yellow]DRY-RUN: No files were moved or posted[/yellow]")


@app.command("run")
def autopost_run(
    queue_dir: str = typer.Option(
        "tweets/queue", "--queue-dir", help="Queue directory path"
    ),
    done_dir: str = typer.Option(
        "tweets/done", "--done-dir", help="Done directory path"
    ),
    pin_file: str = typer.Option("pinned.txt", "--pin-file", help="Pinned tweets file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only, don't post"),
    max_tweets: int = typer.Option(
        10, "--max-tweets", help="Maximum tweets to process"
    ),
):
    """
    Process tweet queue and post to X/Twitter

    Scans queue directory for .tweet.md and .tweet.txt files,
    processes YAML front-matter, converts Markdown to text,
    posts tweets, and moves files to done directory.
    """
    console.print(
        Panel.fit(
            "[bold blue]🚀 RustRocket X - Twitter Autopost[/bold blue]\n"
            f"Queue: {queue_dir}\n"
            f"Done: {done_dir}\n"
            f"Dry-run: {'Yes' if dry_run else 'No'}"
        )
    )

    # Setup paths and directories
    queue_path, done_path, log_file = setup_directories(queue_dir, done_dir)
    pin_file_path = Path(pin_file)

    # Find tweet files
    tweet_files = discover_tweet_files(queue_path, max_tweets)

    if not tweet_files:
        console.print("[yellow]No tweet files found in queue directory[/yellow]")
        return

    # Display queue status
    display_queue_status(tweet_files, dry_run)

    # Initialize Twitter client
    twitter_client = get_twitter_client(dry_run=dry_run)

    # Load pinned tweets
    pinned_tweets = load_pinned_tweets(pin_file_path)
    console.print(f"\n[dim]Currently pinned tweets: {len(pinned_tweets)}[/dim]")

    # Process all tweets
    success_count, error_count = process_all_tweets(
        tweet_files, twitter_client, dry_run, log_file, pin_file_path, done_path
    )

    # Display summary
    display_summary(success_count, error_count, dry_run, log_file)


@app.command("status")
def autopost_status(
    queue_dir: str = typer.Option(
        "tweets/queue", "--queue-dir", help="Queue directory path"
    ),
    done_dir: str = typer.Option(
        "tweets/done", "--done-dir", help="Done directory path"
    ),
):
    """
    Show autopost status and queue information
    """
    console.print(Panel.fit("[bold blue]📊 Autopost Status[/bold blue]"))

    queue_path = Path(queue_dir)
    done_path = Path(done_dir)

    # Count files in queue
    queue_files = list(queue_path.glob("*.tweet.*")) if queue_path.exists() else []
    done_files = list(done_path.glob("*.tweet.*")) if done_path.exists() else []

    table = Table(title="File Status")
    table.add_column("Directory", style="cyan")
    table.add_column("Files", style="bold")
    table.add_column("Total Size", style="dim")

    # Queue stats
    if queue_files:
        total_size = sum(f.stat().st_size for f in queue_files)
        table.add_row("Queue", str(len(queue_files)), f"{total_size} bytes")
    else:
        table.add_row("Queue", "0", "0 bytes")

    # Done stats
    if done_files:
        total_size = sum(f.stat().st_size for f in done_files)
        table.add_row("Done", str(len(done_files)), f"{total_size} bytes")
    else:
        table.add_row("Done", "0", "0 bytes")

    console.print(table)

    # Show recent log entries
    log_file = done_path / "autopost.log"
    if log_file.exists():
        console.print(f"\n[bold]Recent activity from {log_file}:[/bold]")
        try:
            with open(log_file, "r") as f:
                lines = f.readlines()[-5:]  # Last 5 entries
                for line in lines:
                    try:
                        entry = json.loads(line.strip())
                        status = "✅" if entry["success"] else "❌"
                        timestamp = entry["timestamp"][:19]  # Remove microseconds
                        console.print(f"{status} {timestamp} - {entry['filename']}")
                    except (json.JSONDecodeError, KeyError):
                        continue
        except Exception as e:
            console.print(f"[yellow]Could not read log: {e}[/yellow]")
    else:
        console.print("\n[dim]No activity log found[/dim]")
