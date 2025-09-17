"""Test TUNACODE.md logging when thoughts are enabled."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_tunacode_loading_message_displayed():
    """Test that TUNACODE.md loading message is logged when found."""
    # Create a temporary directory with TUNACODE.md
    with tempfile.TemporaryDirectory() as tmpdir:
        tunacode_path = Path(tmpdir) / "TUNACODE.md"
        tunacode_content = """# TUNACODE.md

This file provides guidance to AI assistants.

## Build Commands
- Run tests: `make test`
- Run single test: `pytest tests/test_file.py::test_name`
- Lint: `make lint`

## Code Style
- Use type hints for all functions
- Follow PEP 8 conventions
- Prefer guard clauses over nested conditionals
"""
        tunacode_path.write_text(tunacode_content)

        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Mock the logger to capture calls
            with patch("tunacode.core.agents.agent_components.agent_config.logger") as mock_logger:
                from tunacode.core.agents.agent_components import get_or_create_agent
                from tunacode.core.agents.agent_components.agent_config import clear_all_caches
                from tunacode.core.state import StateManager

                # Clear caches to ensure fresh load
                clear_all_caches()

                # Create state manager with thoughts enabled
                state_manager = StateManager()
                state_manager.session.show_thoughts = True

                # Create agent (this should log the message)
                get_or_create_agent("openai:gpt-4", state_manager)

                # Check that the logger was called with the expected message
                mock_logger.info.assert_called_with("📄 TUNACODE.md located: Loading context...")

        finally:
            os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_tunacode_not_found_message():
    """Test that TUNACODE.md not found message is logged when file doesn't exist."""
    # Create a temporary directory WITHOUT TUNACODE.md
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Mock the logger to capture calls
            with patch("tunacode.core.agents.agent_components.agent_config.logger") as mock_logger:
                from tunacode.core.agents.agent_components import get_or_create_agent
                from tunacode.core.agents.agent_components.agent_config import clear_all_caches
                from tunacode.core.state import StateManager

                # Clear caches to ensure fresh load
                clear_all_caches()

                # Create state manager
                state_manager = StateManager()

                # Create agent (should log not found message)
                get_or_create_agent("openai:gpt-4", state_manager)

                # Check that the logger was called with the expected message
                mock_logger.info.assert_called_with(
                    "📄 TUNACODE.md not found: Using default context"
                )

        finally:
            os.chdir(original_cwd)
