"""Test autopost functionality"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from rustrocket_x.commands.autopost import (
    app,
    load_pinned_tweets,
    markdown_to_text,
    process_tweet_file,
    save_pinned_tweet,
    validate_tweet_length,
)
from rustrocket_x.utils.twitter import TwitterClient, TwitterWriteError


class TestMarkdownProcessing:
    """Test markdown to text conversion"""

    def test_markdown_to_text_simple(self):
        """Test simple markdown conversion"""
        markdown = "# Hello World\n\nThis is **bold** text."
        result = markdown_to_text(markdown)
        assert "Hello World" in result
        assert "bold" in result
        assert "#" not in result
        assert "**" not in result

    def test_markdown_to_text_with_links(self):
        """Test markdown with links"""
        markdown = "Check out [our website](https://example.com)!"
        result = markdown_to_text(markdown)
        assert "Check out our website!" in result
        assert "https://example.com" not in result

    def test_markdown_to_text_with_code(self):
        """Test markdown with code blocks"""
        markdown = "Here's some `code` and more text."
        result = markdown_to_text(markdown)
        assert "code" in result
        assert "`" not in result

    def test_validate_tweet_length(self):
        """Test tweet length validation"""
        assert validate_tweet_length("Short tweet")
        assert validate_tweet_length("x" * 280)
        assert not validate_tweet_length("x" * 281)


class TestPinnedTweets:
    """Test pinned tweets functionality"""

    def test_load_pinned_tweets_nonexistent(self, tmp_path):
        """Test loading from non-existent file"""
        pin_file = tmp_path / "nonexistent.txt"
        result = load_pinned_tweets(pin_file)
        assert result == []

    def test_load_pinned_tweets_existing(self, tmp_path):
        """Test loading from existing file"""
        pin_file = tmp_path / "pinned.txt"
        pin_file.write_text("12345\n67890\n\n# comment\n")

        result = load_pinned_tweets(pin_file)
        assert result == ["12345", "67890", "# comment"]

    def test_save_pinned_tweet(self, tmp_path):
        """Test saving pinned tweet"""
        pin_file = tmp_path / "pinned.txt"

        save_pinned_tweet(pin_file, "12345")
        save_pinned_tweet(pin_file, "67890")

        content = pin_file.read_text()
        assert "12345\n" in content
        assert "67890\n" in content


class TestTwitterClient:
    """Test Twitter client functionality"""

    def test_twitter_client_dry_run(self):
        """Test client in dry-run mode"""
        client = TwitterClient(dry_run=True)
        assert client.dry_run
        assert client.session is None

    @patch("rustrocket_x.utils.twitter.settings")
    def test_twitter_client_missing_credentials(self, mock_settings):
        """Test client with missing credentials"""
        mock_settings.x_api_key = ""
        mock_settings.x_api_secret = ""
        mock_settings.x_access_token = ""
        mock_settings.x_access_token_secret = ""

        client = TwitterClient(dry_run=False)
        assert client.session is None

    def test_post_tweet_dry_run(self):
        """Test posting tweet in dry-run mode"""
        client = TwitterClient(dry_run=True)
        result = client.post_tweet("Test tweet")
        assert result == "dry_run_tweet_id_12345"

    def test_post_tweet_too_long(self):
        """Test posting tweet that's too long"""
        client = TwitterClient(dry_run=True)
        long_text = "x" * 281

        with pytest.raises(TwitterWriteError, match="Tweet too long"):
            client.post_tweet(long_text)

    def test_pin_tweet_dry_run(self):
        """Test pinning tweet in dry-run mode"""
        client = TwitterClient(dry_run=True)
        result = client.pin_tweet("12345")
        assert result is True


class TestFileProcessing:
    """Test tweet file processing"""

    def test_process_tweet_file_markdown(self, tmp_path):
        """Test processing markdown file"""
        tweet_file = tmp_path / "test.tweet.md"
        tweet_file.write_text(
            """---
pin: true
tags: ["test"]
---

# Test Tweet

This is a **test** tweet with [link](https://example.com).
"""
        )

        client = TwitterClient(dry_run=True)
        result = process_tweet_file(tweet_file, client, dry_run=True)

        assert result["success"]
        assert result["tweet_id"] == "dry_run_tweet_id_12345"
        assert "Test Tweet" in result["text"]
        assert result["metadata"]["pin"] is True
        assert result["pinned"] is True

    def test_process_tweet_file_text(self, tmp_path):
        """Test processing text file"""
        tweet_file = tmp_path / "test.tweet.txt"
        tweet_file.write_text(
            """---
reply_to: "12345"
---

Simple text tweet for testing purposes.
"""
        )

        client = TwitterClient(dry_run=True)
        result = process_tweet_file(tweet_file, client, dry_run=True)

        assert result["success"]
        assert result["metadata"]["reply_to"] == "12345"
        assert "Simple text tweet" in result["text"]

    def test_process_tweet_file_too_long(self, tmp_path):
        """Test processing file with tweet too long"""
        tweet_file = tmp_path / "test.tweet.txt"
        long_text = "x" * 281
        tweet_file.write_text(f"---\n---\n\n{long_text}")

        client = TwitterClient(dry_run=True)
        result = process_tweet_file(tweet_file, client, dry_run=True)

        assert not result["success"]
        assert "Tweet too long" in result["error"]

    def test_process_tweet_file_invalid_yaml(self, tmp_path):
        """Test processing file with invalid YAML"""
        tweet_file = tmp_path / "test.tweet.txt"
        tweet_file.write_text(
            """---
invalid: yaml: syntax:
---

Tweet content
"""
        )

        client = TwitterClient(dry_run=True)
        result = process_tweet_file(tweet_file, client, dry_run=True)

        assert not result["success"]
        assert "error" in result


class TestAutopostCommands:
    """Test autopost CLI commands"""

    def test_autopost_run_dry_run_empty_queue(self, tmp_path):
        """Test autopost run with empty queue"""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                app,
                [
                    "run",
                    "--queue-dir",
                    str(tmp_path / "queue"),
                    "--done-dir",
                    str(tmp_path / "done"),
                    "--dry-run",
                ],
            )

            assert result.exit_code == 0
            assert "No tweet files found" in result.stdout

    def test_autopost_run_dry_run_with_tweets(self, tmp_path):
        """Test autopost run with tweets in queue"""
        runner = CliRunner()

        # Create queue directory and tweet file
        queue_dir = tmp_path / "queue"
        queue_dir.mkdir()

        tweet_file = queue_dir / "test.tweet.txt"
        tweet_file.write_text(
            """---
pin: false
---

Test tweet content for dry run.
"""
        )

        result = runner.invoke(
            app,
            [
                "run",
                "--queue-dir",
                str(queue_dir),
                "--done-dir",
                str(tmp_path / "done"),
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Found 1 tweet file(s)" in result.stdout
        assert "DRY-RUN MODE" in result.stdout
        assert "Successful: 1" in result.stdout
        assert "Errors: 0" in result.stdout

    def test_autopost_run_max_tweets_limit(self, tmp_path):
        """Test autopost run with max tweets limit"""
        runner = CliRunner()

        # Create queue directory and multiple tweet files
        queue_dir = tmp_path / "queue"
        queue_dir.mkdir()

        for i in range(5):
            tweet_file = queue_dir / f"test{i}.tweet.txt"
            tweet_file.write_text(
                f"""---
---

Test tweet {i} content.
"""
            )

        result = runner.invoke(
            app,
            [
                "run",
                "--queue-dir",
                str(queue_dir),
                "--done-dir",
                str(tmp_path / "done"),
                "--max-tweets",
                "3",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Found 3 tweet file(s)" in result.stdout  # Should be limited to 3

    def test_autopost_status_empty(self, tmp_path):
        """Test autopost status with empty directories"""
        runner = CliRunner()

        result = runner.invoke(
            app,
            [
                "status",
                "--queue-dir",
                str(tmp_path / "queue"),
                "--done-dir",
                str(tmp_path / "done"),
            ],
        )

        assert result.exit_code == 0
        assert "File Status" in result.stdout
        assert "No activity log found" in result.stdout

    def test_autopost_status_with_files(self, tmp_path):
        """Test autopost status with files"""
        runner = CliRunner()

        # Create directories and files
        queue_dir = tmp_path / "queue"
        done_dir = tmp_path / "done"
        queue_dir.mkdir()
        done_dir.mkdir()

        # Add some files
        (queue_dir / "pending.tweet.txt").write_text("Pending tweet")
        (done_dir / "completed.tweet.txt").write_text("Completed tweet")

        # Add log file
        log_file = done_dir / "autopost.log"
        log_entry = {
            "timestamp": "2025-06-24T12:00:00Z",
            "filename": "test.tweet.txt",
            "tweet_id": "12345",
            "success": True,
        }
        log_file.write_text(json.dumps(log_entry) + "\n")

        result = runner.invoke(
            app, ["status", "--queue-dir", str(queue_dir), "--done-dir", str(done_dir)]
        )

        assert result.exit_code == 0
        assert "File Status" in result.stdout
        assert "Recent activity" in result.stdout


class TestIntegration:
    """Integration tests"""

    def test_full_pipeline_dry_run(self, tmp_path):
        """Test full pipeline from queue to done (dry-run)"""
        runner = CliRunner()

        # Setup directories
        queue_dir = tmp_path / "queue"
        done_dir = tmp_path / "done"
        queue_dir.mkdir()
        done_dir.mkdir()

        # Create test tweets
        tweet1 = queue_dir / "tweet1.tweet.md"
        tweet1.write_text(
            """---
pin: true
tags: ["integration", "test"]
---

# Integration Test

This is a **test** of the integration pipeline.

#Testing #RustRocket
"""
        )

        tweet2 = queue_dir / "tweet2.tweet.txt"
        tweet2.write_text(
            """---
reply_to: "67890"
---

Reply tweet for integration testing.
"""
        )

        # Run autopost
        result = runner.invoke(
            app,
            [
                "run",
                "--queue-dir",
                str(queue_dir),
                "--done-dir",
                str(done_dir),
                "--pin-file",
                str(tmp_path / "pinned.txt"),
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Found 2 tweet file(s)" in result.stdout
        assert "Successful: 2" in result.stdout
        assert "Errors: 0" in result.stdout
        assert "DRY-RUN" in result.stdout

        # Check that files are still in queue (dry-run)
        assert tweet1.exists()
        assert tweet2.exists()

        # Check status
        status_result = runner.invoke(
            app, ["status", "--queue-dir", str(queue_dir), "--done-dir", str(done_dir)]
        )

        assert status_result.exit_code == 0
        assert "2" in status_result.stdout  # 2 files in queue

    @patch("rustrocket_x.utils.twitter.settings")
    def test_authentication_check(self, mock_settings):
        """Test that authentication is properly checked"""
        # Mock settings with incomplete credentials
        mock_settings.x_api_key = "test_key"
        mock_settings.x_api_secret = ""  # Missing secret
        mock_settings.x_access_token = "test_token"
        mock_settings.x_access_token_secret = "test_secret"

        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test tweet
            Path("tweets/queue").mkdir(parents=True)
            tweet_file = Path("tweets/queue/test.tweet.txt")
            tweet_file.write_text("---\n---\n\nTest tweet")

            # This should work in dry-run even with bad credentials
            result = runner.invoke(app, ["run", "--dry-run"])

            assert result.exit_code == 0
            assert "Successful: 1" in result.stdout
