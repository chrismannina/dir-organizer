"""Models for representing file metadata."""

from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path


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
    
    @property
    def full_path(self) -> str:
        """Get the full path as a string."""
        return str(self.path)
    
    @property
    def is_text_file(self) -> bool:
        """Check if this is a text file based on MIME type."""
        return self.mime_type.startswith('text/') or 'script' in self.mime_type


@dataclass
class FileAnalysis:
    """Represents analysis results for a file."""
    
    path: Path
    tags: List[str] = field(default_factory=list)
    suggested_folder: str = "Other"
    description: str = ""
    
    @property
    def full_path(self) -> str:
        """Get the full path as a string."""
        return str(self.path)


@dataclass
class OrganizationMove:
    """Represents a file move operation in an organization plan."""
    
    source: Path
    destination: Path
    description: str
    tags: List[str] 