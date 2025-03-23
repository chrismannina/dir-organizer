"""Models for representing file metadata."""

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FileMetadata:
    """Represents metadata for a file."""

    path: Path
    name: str
    extension: str
    mime_type: str
    size: int
    created: datetime
    modified: datetime
    content: Optional[str] = None
    category: str = "Other"

    @property
    def full_path(self) -> str:
        """Get the full path as a string."""
        return str(self.path)

    @property
    def is_text_file(self) -> bool:
        """Check if this is a text file based on MIME type."""
        return self.mime_type.startswith("text/") or "script" in self.mime_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "path": str(self.path),
            "name": self.name,
            "extension": self.extension,
            "mime_type": self.mime_type,
            "size": self.size,
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat(),
            "content": self.content,
            "category": self.category,
        }


@dataclass
class FileAnalysis:
    """Represents analysis results for a file."""

    path: Path
    tags: List[str] = field(default_factory=list)
    suggested_folder: str = "Other"
    description: str = ""
    category: str = "Other"

    @property
    def full_path(self) -> str:
        """Get the full path as a string."""
        return str(self.path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "path": str(self.path),
            "tags": self.tags,
            "suggested_folder": self.suggested_folder,
            "description": self.description,
            "category": self.category,
        }


@dataclass
class OrganizationMove:
    """Represents a file move operation in an organization plan."""

    source: Path
    destination: Path
    description: str
    tags: List[str]
    category: str = "Other"


class MetadataStore:
    """Store file metadata and analysis results in SQLite."""

    def __init__(self, db_path: str = None):
        """
        Initialize the metadata store.

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            # Use in-memory database
            self.conn = sqlite3.connect(":memory:")
        else:
            self.conn = sqlite3.connect(db_path)

        self._setup_tables()

    def _setup_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Create file_metadata table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS file_metadata (
            path TEXT PRIMARY KEY,
            name TEXT,
            extension TEXT,
            mime_type TEXT,
            size INTEGER,
            created TEXT,
            modified TEXT,
            content TEXT,
            category TEXT
        )
        """
        )

        # Create file_analysis table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS file_analysis (
            path TEXT PRIMARY KEY,
            tags TEXT,
            suggested_folder TEXT,
            description TEXT,
            category TEXT,
            FOREIGN KEY (path) REFERENCES file_metadata(path)
        )
        """
        )

        self.conn.commit()

    def save_metadata(self, metadata: FileMetadata):
        """Save file metadata to the database."""
        cursor = self.conn.cursor()
        data = metadata.to_dict()

        # Create placeholders and values for SQL query
        placeholders = ", ".join(["?"] * len(data))
        columns = ", ".join(data.keys())
        values = list(data.values())

        query = (
            f"INSERT OR REPLACE INTO file_metadata ({columns}) VALUES ({placeholders})"
        )
        cursor.execute(query, values)
        self.conn.commit()

    def save_analysis(self, analysis: FileAnalysis):
        """Save file analysis to the database."""
        cursor = self.conn.cursor()
        data = analysis.to_dict()

        # Convert tags list to JSON string
        data["tags"] = json.dumps(data["tags"])

        # Create placeholders and values for SQL query
        placeholders = ", ".join(["?"] * len(data))
        columns = ", ".join(data.keys())
        values = list(data.values())

        query = (
            f"INSERT OR REPLACE INTO file_analysis ({columns}) VALUES ({placeholders})"
        )
        cursor.execute(query, values)
        self.conn.commit()

    def get_all_analysis(self) -> List[Dict[str, Any]]:
        """Get all file analysis results."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
        SELECT f.path, f.name, f.extension, f.mime_type, f.category,
               a.tags, a.description, a.suggested_folder
        FROM file_metadata f
        JOIN file_analysis a ON f.path = a.path
        """
        )

        results = []
        for row in cursor.fetchall():
            result = {
                "path": row[0],
                "name": row[1],
                "extension": row[2],
                "mime_type": row[3],
                "category": row[4],
                "tags": json.loads(row[5]),
                "description": row[6],
                "suggested_folder": row[7],
            }
            results.append(result)

        return results

    def close(self):
        """Close the database connection."""
        self.conn.close()
