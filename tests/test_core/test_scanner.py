"""Tests for the scanner module."""

from llm_organizer.core.scanner import DirectoryScanner


def test_scanner_init():
    """Test scanner initialization."""
    scanner = DirectoryScanner()
    assert scanner.exclude_patterns == []

    scanner = DirectoryScanner(exclude_patterns=["*.tmp"])
    assert scanner.exclude_patterns == ["*.tmp"]


def test_scanner_scan_directory(test_files):
    """Test scanning a directory."""
    scanner = DirectoryScanner()

    # Test recursive scanning
    files = scanner.scan_directory(test_files, recursive=True)
    # Should find at least 5 files (excluding hidden files)
    assert len(files) >= 5

    # Check that all files have metadata
    for file_meta in files:
        assert "path" in file_meta
        assert "name" in file_meta
        assert "extension" in file_meta
        assert "size" in file_meta
        assert "created" in file_meta
        assert "modified" in file_meta

    # Test non-recursive scanning
    files = scanner.scan_directory(test_files, recursive=False)
    # Should find only files in the root directory (not nested)
    assert len(files) <= 3  # document.txt, notes.md, script.py

    # Test with exclusion pattern
    scanner = DirectoryScanner(exclude_patterns=["*.py"])
    files = scanner.scan_directory(test_files, recursive=True)

    # Verify no .py files are included
    py_files = [f for f in files if f["extension"] == ".py"]
    assert len(py_files) == 0


def test_scanner_exclude_patterns(test_files):
    """Test excluding files with patterns."""
    # Create scanner with exclude patterns
    scanner = DirectoryScanner(exclude_patterns=["*.md", "nested/*"])

    # Scan directory
    files = scanner.scan_directory(test_files, recursive=True)

    # Check if patterns were applied
    for file_meta in files:
        assert file_meta["extension"] != ".md"
        assert not str(file_meta["path"]).startswith(str(test_files / "nested"))


def test_scanner_content_extraction(test_files):
    """Test content extraction from files."""
    scanner = DirectoryScanner()

    # Scan directory
    files = scanner.scan_directory(test_files, recursive=False)

    # Find a text file
    txt_file = next((f for f in files if f["extension"] == ".txt"), None)
    assert txt_file is not None

    # Check that content was extracted
    assert txt_file["content"] is not None
    assert "test document" in txt_file["content"].lower()
