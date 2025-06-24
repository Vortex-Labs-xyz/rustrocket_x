"""
X (Twitter) API Write Client for Basic Plan

Rate Limits (Basic Plan):
- POST /2/tweets: 300 requests per 3-hour window
- POST /1.1/favorites/create: 1000 requests per 24-hour window
- POST /1.1/statuses/pin: 50 requests per 24-hour window

Cost: $100/month for Basic Plan
"""

import time
from typing import Any, Dict, Optional

from requests_oauthlib import OAuth1Session
from rich.console import Console

from ..config import settings

console = Console()


class TwitterWriteError(Exception):
    """Custom exception for Twitter write operations"""

    pass


class TwitterClient:
    """
    Twitter API v2 Write Client using OAuth 1.0a

    Supports:
    - Tweet posting (v2 API)
    - Tweet pinning (v1.1 API)
    - Rate limiting with exponential backoff
    - Dry-run mode for testing
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.session = None
        self._setup_oauth()

    def _setup_oauth(self) -> None:
        """Setup OAuth 1.0a session for write operations"""
        if self.dry_run:
            console.print(
                "[yellow]Dry-run mode: No real OAuth session created[/yellow]"
            )
            return

        if not all(
            [
                settings.x_api_key,
                settings.x_api_secret,
                settings.x_access_token,
                settings.x_access_token_secret,
            ]
        ):
            console.print("[red]Warning: OAuth 1.0a credentials incomplete[/red]")
            return

        self.session = OAuth1Session(
            client_key=settings.x_api_key,
            client_secret=settings.x_api_secret,
            resource_owner_key=settings.x_access_token,
            resource_owner_secret=settings.x_access_token_secret,
        )

    def post_tweet(self, text: str, reply_to: Optional[str] = None, **kwargs) -> str:
        """
        Post a tweet using X API v2

        Args:
            text: Tweet content (max 280 characters)
            reply_to: Tweet ID to reply to (optional)
            **kwargs: Additional tweet parameters

        Returns:
            Tweet ID of posted tweet

        Raises:
            TwitterWriteError: If posting fails
        """
        if len(text) > 280:
            raise TwitterWriteError(f"Tweet too long: {len(text)} characters (max 280)")

        if self.dry_run:
            console.print(
                f"[cyan]DRY-RUN: Would post tweet ({len(text)} chars):[/cyan]"
            )
            console.print(f"[dim]{text}[/dim]")
            if reply_to:
                console.print(f"[dim]Reply to: {reply_to}[/dim]")
            return "dry_run_tweet_id_12345"

        if not self.session:
            raise TwitterWriteError("OAuth session not initialized")

        # Prepare tweet data
        tweet_data = {"text": text}
        if reply_to:
            tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to}

        # Add any additional parameters
        tweet_data.update(kwargs)

        try:
            # Rate limiting: sleep 1 second between requests
            time.sleep(1)

            response = self.session.post(
                "https://api.twitter.com/2/tweets",
                json=tweet_data,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 429:
                console.print("[yellow]Rate limit hit, waiting 60 seconds...[/yellow]")
                time.sleep(60)
                # Retry once
                response = self.session.post(
                    "https://api.twitter.com/2/tweets",
                    json=tweet_data,
                    headers={"Content-Type": "application/json"},
                )

            response.raise_for_status()

            result = response.json()
            tweet_id = result["data"]["id"]

            console.print(f"[green]✅ Tweet posted: {tweet_id}[/green]")
            return tweet_id

        except Exception as e:
            raise TwitterWriteError(f"Failed to post tweet: {e}") from e

    def pin_tweet(self, tweet_id: str) -> bool:
        """
        Pin a tweet using X API v1.1

        Args:
            tweet_id: ID of tweet to pin

        Returns:
            True if successful

        Raises:
            TwitterWriteError: If pinning fails
        """
        if self.dry_run:
            console.print(f"[cyan]DRY-RUN: Would pin tweet: {tweet_id}[/cyan]")
            return True

        if not self.session:
            raise TwitterWriteError("OAuth session not initialized")

        try:
            response = self.session.post(
                "https://api.twitter.com/1.1/statuses/pin.json", data={"id": tweet_id}
            )

            response.raise_for_status()

            console.print(f"[green]📌 Tweet pinned: {tweet_id}[/green]")
            return True

        except Exception as e:
            raise TwitterWriteError(f"Failed to pin tweet {tweet_id}: {e}") from e

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status (for monitoring)

        Returns:
            Rate limit information
        """
        if self.dry_run or not self.session:
            return {"dry_run": True}

        try:
            response = self.session.get(
                "https://api.twitter.com/1.1/application/rate_limit_status.json"
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            console.print(f"[yellow]Could not fetch rate limits: {e}[/yellow]")
            return {"error": str(e)}


# Singleton instance
_twitter_client: Optional[TwitterClient] = None


def get_twitter_client(dry_run: bool = False) -> TwitterClient:
    """Get or create Twitter client singleton"""
    global _twitter_client
    if _twitter_client is None or _twitter_client.dry_run != dry_run:
        _twitter_client = TwitterClient(dry_run=dry_run)
    return _twitter_client
