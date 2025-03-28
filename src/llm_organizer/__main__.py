#!/usr/bin/env python
"""Command-line interface for the LLM Directory Organizer."""

import sys

import click
from rich.console import Console

from llm_organizer.cli.commands import (
    migrate_command,
    organize_command,
    test_api_command,
    undo_command,
)

console = Console()


@click.group()
@click.version_option()
def cli():
    """LLM-Powered Directory Organizer.

    Organize your files intelligently using AI.
    """


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option(
    "--recursive/--no-recursive", default=True, help="Scan directories recursively"
)
@click.option(
    "--preview/--no-preview", default=True, help="Preview changes before applying"
)
@click.option(
    "--exclude", "-e", multiple=True, help="Patterns of files or directories to exclude"
)
@click.option(
    "--exclude-file",
    type=click.Path(exists=True, dir_okay=False),
    help="YAML file containing exclusion patterns",
)
@click.option(
    "--open-report/--no-open-report",
    default=False,
    help="Automatically open the HTML report in browser",
)
@click.option(
    "--intelligent/--no-intelligent",
    default=False,
    help="Use intelligent organization based on all files together",
)
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to configuration file"
)
def organize(
    directory,
    recursive,
    preview,
    exclude,
    exclude_file,
    open_report,
    intelligent,
    config=None,
):
    """Organize files in DIRECTORY using AI."""
    organize_command(
        directory,
        recursive,
        preview,
        exclude,
        exclude_file,
        open_report,
        intelligent,
        config,
    )


@cli.command()
def undo():
    """Undo the last organization operation."""
    undo_command()


@cli.command()
def test_api():
    """Test the connection to the OpenAI API."""
    test_api_command()


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
def migrate(directory):
    """Migrate organizer files in DIRECTORY to hidden folder."""
    migrate_command(directory)


def main():
    """Run the CLI application."""
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
