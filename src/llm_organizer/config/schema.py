"""Configuration schema for the LLM Organizer."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class LLMConfig(BaseModel):
    """Configuration for the language model."""
    
    api_key: str = Field(..., description="API key for the language model service")
    model_name: str = Field("gpt-3.5-turbo", description="Name of the model to use")
    max_tokens: int = Field(4096, description="Maximum tokens to use in API calls")
    temperature: float = Field(0.7, description="Sampling temperature")
    
    @validator('api_key')
    def api_key_must_not_be_empty(cls, v):
        """Validate that the API key is not empty."""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v


class ScannerConfig(BaseModel):
    """Configuration for the directory scanner."""
    
    text_extensions: List[str] = Field(
        [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml", ".yml"],
        description="File extensions to treat as text files"
    )
    max_file_size_mb: float = Field(
        10.0, 
        description="Maximum file size in MB for content extraction"
    )
    exclude_patterns: List[str] = Field(
        default_factory=list,
        description="Patterns for files/dirs to exclude"
    )
    exclude_hidden: bool = Field(
        True, 
        description="Whether to exclude hidden files and directories"
    )


class OrganizerConfig(BaseModel):
    """Configuration for the file organizer."""
    
    naming_scheme: str = Field(
        "snake_case", 
        description="Naming scheme for created folders (snake_case, camel_case, pascal_case)"
    )
    max_folder_depth: int = Field(
        3, 
        description="Maximum depth of folder hierarchy"
    )
    preserve_projects: bool = Field(
        True, 
        description="Whether to preserve project directories (git repos, etc.)"
    )
    project_markers: List[str] = Field(
        [".git", "package.json", "pyproject.toml", "Cargo.toml", "Makefile"],
        description="Files/directories that indicate a project directory"
    )


class AppConfig(BaseModel):
    """Main application configuration."""
    
    llm: LLMConfig = Field(default_factory=LLMConfig)
    scanner: ScannerConfig = Field(default_factory=ScannerConfig)
    organizer: OrganizerConfig = Field(default_factory=OrganizerConfig)
    data_dir: str = Field("~/.llm_organizer", description="Directory for application data")
    preview_default: bool = Field(True, description="Whether preview mode is enabled by default")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Extra configuration options") 