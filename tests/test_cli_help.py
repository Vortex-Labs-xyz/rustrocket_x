"""Test CLI help functionality"""

import subprocess
import sys
from pathlib import Path


def test_cli_help():
    """Test that the CLI help command exits with code 0"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent

    # Run the CLI help command
    result = subprocess.run(
        [sys.executable, "-m", "rustrocket_x.cli", "--help"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    # Check that it exits successfully
    assert result.returncode == 0
    assert "rustrocket_x" in result.stdout
    assert "metrics" in result.stdout


def test_cli_version():
    """Test that the CLI version command works"""
    project_root = Path(__file__).parent.parent

    result = subprocess.run(
        [sys.executable, "-m", "rustrocket_x.cli", "--version"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "0.1.0" in result.stdout
