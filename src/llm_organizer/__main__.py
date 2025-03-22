#!/usr/bin/env python
"""Command-line interface for the LLM Directory Organizer."""

import os
import sys
import click
from rich.console import Console

from llm_organizer.config.defaults import load_config
from llm_organizer.cli.commands import organize_command, undo_command, test_api_command


console = Console()


@click.group()
@click.version_option()
def cli():
    """LLM-Powered Directory Organizer.
    
    Organize your files intelligently using AI.
    """
    pass


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive/--no-recursive', default=True, help='Scan directories recursively')
@click.option('--preview/--no-preview', default=True, help='Preview changes before applying')
@click.option('--exclude', '-e', multiple=True, help='Patterns of files or directories to exclude')
@click.option('--exclude-file', type=click.Path(exists=True, dir_okay=False), help='YAML file containing exclusion patterns')
@click.option('--open-report/--no-open-report', default=False, help='Automatically open the HTML report in browser')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
def organize(directory, recursive, preview, exclude, exclude_file, open_report, config=None):
    """Organize files in a directory using AI."""
    cfg = load_config(config)
    organize_command(
        directory=directory,
        recursive=recursive,
        preview=preview,
        exclude=exclude,
        exclude_file=exclude_file,
        open_report=open_report,
        config=cfg
    )


@cli.command()
def undo():
    """Undo the last organization operation."""
    undo_command()


@cli.command()
def test_api():
    """Test OpenAI API connection."""
    cfg = load_config()
    test_api_command(config=cfg)


def main():
    """Main entry point for the application."""
    try:
        cli()
    except Exception as e:
        console.print(f"\n❌ Error: {str(e)}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main() 