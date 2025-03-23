"""Implementation of CLI commands."""

import os
import webbrowser
from typing import List, Optional

import yaml
from rich.console import Console
from rich.prompt import Confirm

from llm_organizer.config.schema import AppConfig
from llm_organizer.core.indexer import FileIndexer
from llm_organizer.core.organizer import FileOrganizer
from llm_organizer.core.scanner import DirectoryScanner
from llm_organizer.utils.logger import OperationLogger

console = Console()


def load_exclusions(exclude_file: str) -> List[str]:
    """
    Load exclusion patterns from a YAML file.

    Args:
        exclude_file: Path to the YAML file containing exclusion patterns

    Returns:
        List of exclusion patterns
    """
    patterns = []

    try:
        with open(exclude_file, "r") as f:
            data = yaml.safe_load(f)

        if not data:
            console.print("[yellow]Warning:[/yellow] Empty exclusion file")
            return patterns

        if isinstance(data, list):
            patterns = data
        elif isinstance(data, dict) and "exclusions" in data:
            patterns = data["exclusions"]
        else:
            console.print("[yellow]Warning:[/yellow] Invalid exclusion file format")

    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Error loading exclusion file: {e}")

    return patterns


def organize_command(
    directory: str,
    recursive: bool = True,
    preview: bool = True,
    exclude: Optional[List[str]] = None,
    exclude_file: Optional[str] = None,
    open_report: bool = False,
    intelligent: bool = False,
    config: Optional[AppConfig] = None,
) -> None:
    """
    Organize files in a directory using AI.

    Args:
        directory: Path to directory to organize
        recursive: Whether to scan recursively
        preview: Whether to preview changes before executing
        exclude: List of patterns to exclude
        exclude_file: Path to YAML file with exclusion patterns
        open_report: Whether to open the HTML report automatically
        intelligent: Whether to use intelligent schema for organization
        config: Configuration object

    The intelligent option uses a holistic approach to analyze all files together,
    creating a cohesive organization plan with categories and subcategories based on
    file relationships, instead of organizing each file individually.
    """
    try:
        if config is None:
            from llm_organizer.config.defaults import load_config

            config = load_config()

        # Validate API key
        if not config.llm.api_key:
            console.print(
                "❌ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable or add it to your configuration.",
                style="red",
            )
            return

        # Show a message about API key being used
        api_key = config.llm.api_key
        masked_key = f"{api_key[:10]}...{api_key[-4:]}"
        console.print(f"\n🔑 Using OpenAI API key: {masked_key}", style="blue")
        console.print(f"Using model: {config.llm.model_name}", style="blue")

        # Combine exclusions from command line and file
        exclusions = list(exclude) if exclude else []
        if exclude_file:
            file_exclusions = load_exclusions(exclude_file)
            exclusions.extend(file_exclusions)
            console.print(
                f"\n📄 Loaded {len(file_exclusions)} exclusion patterns from {exclude_file}",
                style="blue",
            )

        # Add configured exclusions
        if config.scanner.exclude_patterns:
            exclusions.extend(config.scanner.exclude_patterns)

        # Initialize components
        scanner = DirectoryScanner(exclude_patterns=exclusions)
        indexer = FileIndexer(
            {"openai_api_key": config.llm.api_key, "model_name": config.llm.model_name}
        )
        organizer = FileOrganizer()
        logger = OperationLogger()

        # Display exclusion patterns if any
        if exclusions:
            console.print("\n🚫 Excluding patterns:", style="yellow")
            for pattern in exclusions[
                :10
            ]:  # Show only first 10 to avoid cluttering the console
                console.print(f"  - {pattern}")
            if len(exclusions) > 10:
                console.print(f"  ... and {len(exclusions) - 10} more patterns")

            # Also exclude common directories automatically
            console.print(
                "\n🚫 Also excluding common system directories:", style="yellow"
            )
            console.print("  - venv, node_modules, .git, __pycache__, dist, build")

        # Scan directory
        try:
            console.print(f"\n📂 Scanning directory: {directory}")
            files_metadata = scanner.scan_directory(directory, recursive)

            if not files_metadata:
                console.print("❌ No files found to organize!", style="red")
                return

            console.print(
                f"📊 Found {len(files_metadata)} files to analyze", style="green"
            )
        except Exception as e:
            console.print(f"❌ Error scanning directory: {str(e)}", style="red")
            return

        # Test API connection before processing
        console.print("\n🔍 Testing API connection before analysis...")
        if not indexer.test_api_connection():
            console.print(
                "❌ API connection failed. Please check your API key and try again.",
                style="red",
            )
            console.print(
                "Run 'llm-organizer test-api' for more detailed diagnostics.",
                style="yellow",
            )
            return

        # Analyze files
        console.print("\n🔍 Analyzing files with AI...")
        analysis_results = indexer.analyze_files(
            scanner.get_files() if hasattr(scanner, "get_files") else files_metadata
        )

        # Generate organization plan
        console.print("\n📋 Generating organization plan...")
        organization_plan = organizer.generate_plan(
            analysis_results, use_intelligent_schema=intelligent
        )

        # Display preview
        report_path = organizer.display_plan(organization_plan)

        # Auto open the report in browser if requested
        if open_report and report_path:
            file_url = f"file://{os.path.abspath(report_path)}"
            console.print(f"\n🌐 Opening report in browser: {file_url}", style="blue")
            webbrowser.open(file_url)

        if preview:
            if Confirm.ask("\n❓ Do you want to proceed with these changes?"):
                # Execute organization
                console.print("\n🔄 Executing organization plan...")
                operations = organizer.execute_plan(organization_plan)

                # Log operations
                logger.log_operations(operations)

                # Generate master TOC
                toc_path = organizer.generate_toc(organization_plan)

                console.print(
                    f"\n✅ Organization complete! Master TOC saved to: {toc_path}",
                    style="green",
                )
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

            console.print(
                f"\n✅ Organization complete! Master TOC saved to: {toc_path}",
                style="green",
            )

    except Exception as e:
        console.print(f"\n❌ Error: {str(e)}", style="red")
        console.print(
            "\nIf this is an API error, you can run 'llm-organizer test-api' to diagnose API connection issues.",
            style="yellow",
        )
        raise


def undo_command() -> None:
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


def test_api_command(config: Optional[AppConfig] = None) -> None:
    """Test OpenAI API connection."""
    try:
        console.print("\n🔍 Testing OpenAI API connection...", style="blue")

        if config is None:
            from llm_organizer.config.defaults import load_config

            config = load_config()

        if not config.llm.api_key:
            console.print("❌ OpenAI API key not found in configuration.", style="red")
            console.print(
                "Please set the OPENAI_API_KEY environment variable or add it to your configuration.",
                style="yellow",
            )
            return

        # Show masked API key
        api_key = config.llm.api_key
        masked_key = f"{api_key[:10]}...{api_key[-4:]}"
        console.print(f"Using API key: {masked_key}", style="blue")

        # First, test with direct OpenAI API
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=config.llm.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": "Please respond with 'OpenAI API connection successful'.",
                    },
                ],
                max_tokens=20,
            )
            if response and response.choices and len(response.choices) > 0:
                console.print(
                    "\n✅ Direct OpenAI API connection successful!", style="green"
                )
                console.print(f"Response: {response.choices[0].message.content}")
            else:
                console.print(
                    "\n❌ Error: Received empty response from OpenAI API", style="red"
                )
                return
        except Exception as e:
            console.print(f"\n❌ Error with direct OpenAI API: {str(e)}", style="red")
            return

        # Then, test with llama_index
        console.print("\n🔍 Testing LlamaIndex integration...", style="blue")
        indexer = FileIndexer(
            {"openai_api_key": config.llm.api_key, "model_name": config.llm.model_name}
        )
        if indexer.test_api_connection():
            console.print(
                "\n✅ API setup verified and working correctly!", style="green"
            )
        else:
            console.print(
                "\n❌ Error with LlamaIndex integration. Direct API works but LlamaIndex integration fails.",
                style="red",
            )

    except Exception as e:
        console.print(f"\n❌ Error: {str(e)}", style="red")
        raise
