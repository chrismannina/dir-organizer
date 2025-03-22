"""Pytest configuration and fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest

from llm_organizer.config.schema import (
    AppConfig,
    LLMConfig,
    OrganizerConfig,
    ScannerConfig,
)


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return AppConfig(
        llm=LLMConfig(
            api_key="test_api_key",
            model_name="test_model",
        ),
        scanner=ScannerConfig(
            text_extensions=[".txt", ".md"],
            max_file_size_mb=1.0,
            exclude_patterns=[".git*"],
            exclude_hidden=True,
        ),
        organizer=OrganizerConfig(
            naming_scheme="snake_case",
            max_folder_depth=2,
            preserve_projects=True,
            project_markers=[".git"],
        ),
        preview_default=True,
    )


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_files(temp_dir):
    """Create test files in the temporary directory."""
    # Create text files
    (temp_dir / "document.txt").write_text("This is a test document.")
    (temp_dir / "notes.md").write_text("# Test Notes\nThis is a test note.")

    # Create a Python file
    (temp_dir / "script.py").write_text("def test():\n    print('Hello, world!')")

    # Create a hidden file
    (temp_dir / ".hidden.txt").write_text("This is a hidden file.")

    # Create a nested directory
    nested_dir = temp_dir / "nested"
    nested_dir.mkdir()
    (nested_dir / "nested_file.txt").write_text("This is a nested file.")

    # Create a project-like directory
    project_dir = temp_dir / "project"
    project_dir.mkdir()
    (project_dir / ".git").mkdir()  # Simulate a git repository
    (project_dir / "code.py").write_text("# Project code")

    return temp_dir
