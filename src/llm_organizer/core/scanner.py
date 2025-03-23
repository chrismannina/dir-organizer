"""Directory scanner module for collecting file metadata."""

import fnmatch
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Pattern

from tqdm import tqdm

# Conditionally import document processing libraries
try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    from docx import Document

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class DirectoryScanner:
    """Handles directory scanning and metadata collection."""

    def __init__(self, exclude_patterns: List[str] = None):
        self.text_extensions = {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
        }
        self.supported_binary = {}
        self.files_metadata = []  # Store files metadata for later retrieval

        # Only add supported binary handlers if libraries are available
        if PDF_AVAILABLE:
            self.supported_binary[".pdf"] = self._extract_pdf_text
        if DOCX_AVAILABLE:
            self.supported_binary[".docx"] = self._extract_docx_text

        self.exclude_patterns = exclude_patterns or []
        self.compiled_patterns = self._compile_patterns(self.exclude_patterns)

    def _compile_patterns(self, patterns: List[str]) -> List[Pattern]:
        """Compile glob patterns to regex patterns."""
        compiled = []
        for pattern in patterns:
            # Check if it's a directory pattern (ending with /*)
            if pattern.endswith("/*"):
                # Convert to a pattern that matches any file in the directory
                dir_pattern = pattern[:-2]
                regex_pattern = f"^.*{re.escape(dir_pattern)}(/|\\\\).*$"
                compiled.append(re.compile(regex_pattern))
            else:
                # Convert glob pattern to regex pattern
                regex_pattern = fnmatch.translate(pattern)
                compiled.append(re.compile(regex_pattern))
        return compiled

    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded based on patterns."""
        path_str = str(path)

        # Check against all patterns
        for pattern in self.compiled_patterns:
            if pattern.match(path_str):
                return True

        # Check common directories to exclude
        common_excludes = [
            "venv",
            "node_modules",
            ".git",
            "__pycache__",
            "dist",
            "build",
        ]
        for exclude in common_excludes:
            if exclude in path_str.split(os.sep):
                return True

        return False

    def scan_directory(self, directory: str, recursive: bool = True) -> List[Dict]:
        """
        Scan a directory and collect metadata for all files.

        Args:
            directory (str): Path to the directory to scan
            recursive (bool): Whether to scan subdirectories

        Returns:
            List[Dict]: List of file metadata dictionaries
        """
        directory_path = Path(directory)
        self.files_metadata = []  # Reset file metadata

        # Get all files in directory
        if recursive:
            all_files = []
            # Use os.walk to be able to skip directories
            for root, dirs, files in os.walk(directory_path):
                root_path = Path(root)

                # Remove excluded directories (modify dirs in-place to prevent recursion)
                dirs[:] = [d for d in dirs if not self._should_exclude(root_path / d)]

                # Add non-excluded files
                for filename in files:
                    file_path = root_path / filename
                    if not self._should_exclude(
                        file_path
                    ) and not file_path.name.startswith("."):
                        all_files.append(file_path)
        else:
            # For non-recursive, just get files in the top directory
            all_files = [
                f
                for f in directory_path.glob("*")
                if f.is_file()
                and not self._should_exclude(f)
                and not f.name.startswith(".")
            ]

        # Process files
        for file_path in tqdm(all_files, desc="Scanning files"):
            try:
                metadata = self._get_file_metadata(file_path)
                if metadata:
                    self.files_metadata.append(metadata)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue

        return self.files_metadata

    def _get_file_metadata(self, file_path: Path) -> Optional[Dict]:
        """
        Get metadata for a single file.

        Args:
            file_path (Path): Path to the file

        Returns:
            Optional[Dict]: File metadata or None if file should be skipped
        """
        try:
            stats = file_path.stat()
            mime_type = self._get_mime_type(file_path)

            metadata = {
                "path": str(file_path),
                "name": file_path.name,
                "extension": file_path.suffix.lower(),
                "size": stats.st_size,
                "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "mime_type": mime_type,
                "content": None,
            }

            # Extract text content if possible
            if metadata["extension"] in self.text_extensions:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        metadata["content"] = f.read()
                except UnicodeDecodeError:
                    metadata["content"] = None

            elif metadata["extension"] in self.supported_binary:
                extractor = self.supported_binary[metadata["extension"]]
                metadata["content"] = extractor(file_path)

            return metadata

        except Exception as e:
            print(f"Error getting metadata for {file_path}: {str(e)}")
            return None

    def _get_mime_type(self, file_path: Path) -> str:
        """Get the MIME type of a file."""
        if MAGIC_AVAILABLE:
            try:
                return magic.from_file(str(file_path), mime=True)
            except Exception:
                pass

        # Fallback to extension-based mime type guess
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".txt", ".md"]:
            return "text/plain"
        elif ext == ".html":
            return "text/html"
        elif ext == ".py":
            return "text/x-python"
        elif ext == ".js":
            return "application/javascript"
        elif ext == ".json":
            return "application/json"
        elif ext == ".pdf":
            return "application/pdf"
        elif ext == ".docx":
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            return "application/octet-stream"

    def _extract_pdf_text(self, file_path: Path) -> Optional[str]:
        """Extract text content from PDF files."""
        if not PDF_AVAILABLE:
            return "PDF library not available"
        try:
            text = []
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text.append(page.extract_text())
            return "\n".join(text)
        except Exception:
            return None

    def _extract_docx_text(self, file_path: Path) -> Optional[str]:
        """Extract text content from DOCX files."""
        if not DOCX_AVAILABLE:
            return "DOCX library not available"
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return None

    def get_files(self) -> List[Dict]:
        """
        Get the file metadata collected during scanning.

        Returns:
            List[Dict]: List of file metadata dictionaries
        """
        return self.files_metadata
