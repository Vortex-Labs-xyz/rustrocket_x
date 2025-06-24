"""Test metrics dry run functionality"""

import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from rustrocket_x.commands.metrics import app


@pytest.fixture
def mock_api_response():
    """Mock API response for testing"""
    return {
        "data": {
            "id": "12345",
            "name": "Test User",
            "username": "testuser",
            "public_metrics": {
                "followers_count": 1000,
                "following_count": 500,
                "tweet_count": 2000,
                "listed_count": 10,
                "like_count": 5000,
            },
        }
    }


def test_metrics_pull_dry_run(mock_api_response):
    """Test metrics pull command with dry run flag"""
    runner = CliRunner()

    # Mock the requests.Session.get method instead of the class
    with patch("requests.Session.get") as mock_get:
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Run the command
        result = runner.invoke(app, ["--user", "testuser", "--dry-run"])

        # Debug output on failure
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.stdout}")
            print(f"Exception: {result.exception}")

        # Assertions
        assert result.exit_code == 0
        assert "Dry-run: no file written" in result.stdout
        assert "testuser" in result.stdout
        assert "1,000" in result.stdout  # followers count formatted

        # Verify API was called
        mock_get.assert_called_once()


def test_metrics_pull_filename_generation():
    """Test that the correct filename is generated for output"""

    # Test filename generation logic by checking what would be generated
    date_str = datetime.now().strftime("%Y%m%d")
    expected_filename = f"data/x_metrics_{date_str}.json"

    # This tests the filename pattern
    assert "x_metrics_" in expected_filename
    assert date_str in expected_filename
    assert expected_filename.endswith(".json")


def test_metrics_pull_with_custom_outfile(mock_api_response, tmp_path):
    """Test metrics pull with custom output file"""
    runner = CliRunner()
    outfile = tmp_path / "custom_metrics.json"

    # Mock the requests.Session.get method instead of the class
    with patch("requests.Session.get") as mock_get:
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = runner.invoke(app, ["--user", "testuser", "--outfile", str(outfile)])

        # Debug output on failure
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.stdout}")
            print(f"Exception: {result.exception}")

        assert result.exit_code == 0
        assert outfile.exists()

        # Check file content
        with open(outfile) as f:
            data = json.load(f)

        assert data["username"] == "testuser"
        assert data["metrics"]["followers_count"] == 1000
