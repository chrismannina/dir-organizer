import os
import magic
import PyPDF2
import docx
import fnmatch
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Pattern
from datetime import datetime
from tqdm import tqdm

class DirectoryScanner:
    """Handles directory scanning and metadata collection."""
    
    def __init__(self, exclude_patterns: List[str] = None):
        self.text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml'}
        self.supported_binary = {'.pdf': self._extract_pdf_text, '.docx': self._extract_docx_text}
        self.exclude_patterns = exclude_patterns or []
        self.compiled_patterns = self._compile_patterns(self.exclude_patterns)
    
    def _compile_patterns(self, patterns: List[str]) -> List[Pattern]:
        """Compile glob patterns to regex patterns for faster matching."""
        compiled = []
        for pattern in patterns:
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
        common_excludes = ['venv', 'node_modules', '.git', '__pycache__', 'dist', 'build']
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
        files_metadata = []
        
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
                    if not self._should_exclude(file_path) and not file_path.name.startswith('.'):
                        all_files.append(file_path)
        else:
            # For non-recursive, just get files in the top directory
            all_files = [
                f for f in directory_path.glob('*') 
                if f.is_file() and not self._should_exclude(f) and not f.name.startswith('.')
            ]
        
        # Process files
        for file_path in tqdm(all_files, desc="Scanning files"):
            try:
                metadata = self._get_file_metadata(file_path)
                if metadata:
                    files_metadata.append(metadata)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
        
        return files_metadata
    
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
            mime_type = magic.from_file(str(file_path), mime=True)
            
            metadata = {
                'path': str(file_path),
                'name': file_path.name,
                'extension': file_path.suffix.lower(),
                'size': stats.st_size,
                'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'mime_type': mime_type,
                'content': None
            }
            
            # Extract text content if possible
            if metadata['extension'] in self.text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        metadata['content'] = f.read()
                except UnicodeDecodeError:
                    metadata['content'] = None
            
            elif metadata['extension'] in self.supported_binary:
                extractor = self.supported_binary[metadata['extension']]
                metadata['content'] = extractor(file_path)
            
            return metadata
            
        except Exception as e:
            print(f"Error getting metadata for {file_path}: {str(e)}")
            return None
    
    def _extract_pdf_text(self, file_path: Path) -> Optional[str]:
        """Extract text content from PDF files."""
        try:
            text = []
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text.append(page.extract_text())
            return '\n'.join(text)
        except Exception:
            return None
    
    def _extract_docx_text(self, file_path: Path) -> Optional[str]:
        """Extract text content from DOCX files."""
        try:
            doc = docx.Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception:
            return None 