#!/usr/bin/env python3

import os
import json
import yaml
import click
from rich.console import Console
from rich.prompt import Confirm
from pathlib import Path
from typing import Dict, List, Optional

from scanner import DirectoryScanner
from indexer import FileIndexer
from organizer import FileOrganizer
from logger import OperationLogger

console = Console()

def load_config() -> dict:
    """Load configuration from environment variables or config file."""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "model_name": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
    }

def load_exclusions(exclude_file: str) -> List[str]:
    """Load exclusion patterns from a YAML file."""
    if not exclude_file or not os.path.exists(exclude_file):
        return []
    
    try:
        with open(exclude_file, 'r') as f:
            content = yaml.safe_load(f)
            
        if not content:
            return []
            
        # If it's a list, return it directly
        if isinstance(content, list):
            return [pattern for pattern in content if isinstance(pattern, str)]
            
        # If it's a dict, look for an 'exclusions' or 'patterns' key
        if isinstance(content, dict):
            for key in ['exclusions', 'patterns', 'exclude']:
                if key in content and isinstance(content[key], list):
                    return [pattern for pattern in content[key] if isinstance(pattern, str)]
                    
        # If we get here, try to extract all string values as patterns
        if isinstance(content, dict):
            return [val for val in content.values() if isinstance(val, str)]
            
        return []
    except Exception as e:
        console.print(f"Error loading exclusion file: {str(e)}", style="red")
        return []

@click.group()
def cli():
    """LLM-Powered Directory Organizer"""
    pass

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive/--no-recursive', default=True, help='Scan directories recursively')
@click.option('--preview/--no-preview', default=True, help='Preview changes before applying')
@click.option('--exclude', '-e', multiple=True, help='Patterns of files or directories to exclude (can be used multiple times)')
@click.option('--exclude-file', type=click.Path(exists=True, dir_okay=False), help='YAML file containing exclusion patterns')
@click.option(
    "--open-report/--no-open-report",
    default=False,
    help="Automatically open the HTML report in browser.",
)
def organize(
    directory: str,
    preview: bool = False,
    recursive: bool = True,
    exclude: List[str] = None,
    exclude_file: str = None,
    open_report: bool = False,
):
    """Organize files in a directory using AI."""
    try:
        config = load_config()
        
        # Combine exclusions from command line and file
        exclusions = list(exclude) if exclude else []
        if exclude_file:
            file_exclusions = load_exclusions(exclude_file)
            exclusions.extend(file_exclusions)
            console.print(f"\n📄 Loaded {len(file_exclusions)} exclusion patterns from {exclude_file}", style="blue")
        
        # Initialize components
        scanner = DirectoryScanner(exclude_patterns=exclusions)
        indexer = FileIndexer(config)
        organizer = FileOrganizer()
        logger = OperationLogger()

        # Display exclusion patterns if any
        if exclusions:
            console.print("\n🚫 Excluding patterns:", style="yellow")
            for pattern in exclusions[:10]:  # Show only first 10 to avoid cluttering the console
                console.print(f"  - {pattern}")
            if len(exclusions) > 10:
                console.print(f"  ... and {len(exclusions) - 10} more patterns")
            
            # Also exclude common directories automatically
            console.print("\n🚫 Also excluding common system directories:", style="yellow")
            console.print("  - venv, node_modules, .git, __pycache__, dist, build")

        # Scan directory
        console.print(f"\n📂 Scanning directory: {directory}")
        files_metadata = scanner.scan_directory(directory, recursive)
        
        if not files_metadata:
            console.print("❌ No files found to organize!", style="red")
            return

        # Index and analyze files
        console.print("\n🔍 Analyzing files with LLM...")
        analysis_results = indexer.analyze_files(files_metadata)
        
        # Generate organization plan
        console.print("\n📋 Generating organization plan...")
        organization_plan = organizer.generate_plan(analysis_results)
        
        if preview:
            console.print("\n📝 Proposed Changes:", style="bold blue")
            report_path = organizer.display_plan(organization_plan)
            
            # Auto open the report in browser if requested
            if open_report and report_path:
                # Construct a file:// URL
                import webbrowser
                file_url = f"file://{os.path.abspath(report_path)}"
                console.print(f"\n🌐 Opening report in browser: {file_url}", style="blue")
                webbrowser.open(file_url)
            
            if Confirm.ask("\n❓ Do you want to proceed with these changes?"):
                # Execute organization
                console.print("\n🔄 Executing organization plan...")
                operations = organizer.execute_plan(organization_plan)
                
                # Log operations
                logger.log_operations(operations)
                
                # Generate master TOC
                toc_path = organizer.generate_toc(organization_plan)
                
                console.print(f"\n✅ Organization complete! Master TOC saved to: {toc_path}", style="green")
            else:
                console.print("Operation cancelled by user.", style="yellow")
                return
        else:
            # Execute organization
            console.print("\n🔄 Executing organization plan...")
            operations = organizer.execute_plan(organization_plan)
            
            # Log operations
            logger.log_operations(operations)
            
            # Generate master TOC
            toc_path = organizer.generate_toc(organization_plan)
            
            console.print(f"\n✅ Organization complete! Master TOC saved to: {toc_path}", style="green")

    except Exception as e:
        console.print(f"\n❌ Error: {str(e)}", style="red")
        raise

@cli.command()
def undo():
    """Undo the last organization operation."""
    try:
        logger = OperationLogger()
        operations = logger.get_last_operations()
        
        if not operations:
            console.print("❌ No previous operations found to undo!", style="yellow")
            return
        
        if Confirm.ask("❓ Do you want to undo the last organization?"):
            console.print("\n🔄 Undoing last organization...")
            logger.undo_operations(operations)
            console.print("✅ Undo complete!", style="green")
        else:
            console.print("Operation cancelled by user.", style="yellow")
            
    except Exception as e:
        console.print(f"\n❌ Error during undo: {str(e)}", style="red")
        raise

if __name__ == '__main__':
    cli() 