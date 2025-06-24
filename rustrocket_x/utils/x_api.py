"""X (Twitter) API client utilities"""

from typing import Any, Dict, Optional

import requests
from rich.console import Console

from ..config import settings

console = Console()


class XAPIClient:
    """Client for X (Twitter) API v2 with Bearer Token authentication"""

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or settings.x_bearer_token
        self.session = requests.Session()
        self._setup_headers()

    def _setup_headers(self) -> None:
        """Setup default headers for API requests"""
        if not self.bearer_token:
            console.print("[red]Warning: No bearer token provided[/red]")
            return

        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json",
            }
        )

    def get_user_by_username(
        self, username: str, user_fields: str = "public_metrics"
    ) -> Dict[str, Any]:
        """Get user information by username

        Args:
            username: Twitter username (without @)
            user_fields: Comma-separated list of user fields to include

        Returns:
            API response as dictionary

        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.BASE_URL}/users/by/username/{username}"
        params = {"user.fields": user_fields}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        return response.json()

    def get_user_metrics(self, username: str) -> Dict[str, Any]:
        """Get public metrics for a user

        Args:
            username: Twitter username (without @)

        Returns:
            User data with public metrics
        """
        return self.get_user_by_username(username, "public_metrics")
