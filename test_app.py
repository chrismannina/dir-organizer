#!/usr/bin/env python3
"""
Comprehensive test script for the LLM Directory Organizer.
This script tests:
1. Environment setup
2. API connectivity
3. File scanning
4. LLM analysis
5. Organization plan generation

Usage:
    python test_app.py
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

# Import application modules
from scanner import DirectoryScanner
from indexer import FileIndexer
from organizer import FileOrganizer
from openai import OpenAI

console = Console()

def test_environment():
    """Test environment setup and dependencies."""
    console.print("\n[bold blue]Testing environment setup...[/bold blue]")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"Python version: {python_version}")
    if sys.version_info < (3, 8):
        console.print("❌ Python 3.8 or higher is required", style="red")
        return False
    else:
        console.print("✅ Python version OK", style="green")
    
    # Check .env file
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    if not api_key:
        console.print("❌ OPENAI_API_KEY not found in .env file", style="red")
        return False
    else:
        masked_key = f"{api_key[:10]}...{api_key[-4:]}"
        console.print(f"✅ API key found: {masked_key}", style="green")
        console.print(f"✅ Model name: {model_name}", style="green")
    
    return True

def test_direct_api():
    """Test direct OpenAI API connection."""
    console.print("\n[bold blue]Testing direct OpenAI API connection...[/bold blue]")
    
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Please respond with 'API connection successful'."}
            ],
            max_tokens=20
        )
        
        if response and response.choices and len(response.choices) > 0:
            console.print("✅ Direct API connection successful", style="green")
            console.print(f"Response: {response.choices[0].message.content}")
            return True
        else:
            console.print("❌ Received empty response from API", style="red")
            return False
    except Exception as e:
        console.print(f"❌ API connection error: {str(e)}", style="red")
        return False

def test_llama_index():
    """Test LlamaIndex integration."""
    console.print("\n[bold blue]Testing LlamaIndex integration...[/bold blue]")
    
    config = {
        'openai_api_key': os.getenv("OPENAI_API_KEY"),
        'model_name': os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    }
    
    try:
        indexer = FileIndexer(config)
        if indexer.test_api_connection():
            console.print("✅ LlamaIndex integration successful", style="green")
            return True
        else:
            console.print("❌ LlamaIndex test failed", style="red")
            return False
    except Exception as e:
        console.print(f"❌ LlamaIndex error: {str(e)}", style="red")
        return False

def test_file_scanning():
    """Test file scanning functionality."""
    console.print("\n[bold blue]Testing file scanning...[/bold blue]")
    
    # Create a temporary test directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Create some test files
        test_files = [
            ("test1.txt", "This is a test document for file organization."),
            ("test2.md", "# Sample Markdown\nThis is a sample markdown file."),
            ("notes.txt", "Important notes for the project."),
            (".hidden.txt", "This is a hidden file that should be excluded.")
        ]
        
        for filename, content in test_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        console.print(f"Created test directory at: {temp_dir}")
        console.print(f"Added {len(test_files)} test files")
        
        # Initialize scanner with default exclusions
        scanner = DirectoryScanner(exclude_patterns=[".hidden*"])
        
        # Scan the directory
        files_metadata = scanner.scan_directory(temp_dir, recursive=True)
        
        # Verify results
        if files_metadata and len(files_metadata) == 3:  # Should exclude the hidden file
            console.print(f"✅ File scanning successful - found {len(files_metadata)} files", style="green")
            for metadata in files_metadata:
                console.print(f"  - {metadata['name']} ({metadata['extension']})")
            return True
        else:
            console.print(f"❌ File scanning failed - expected 3 files, found {len(files_metadata) if files_metadata else 0}", style="red")
            return False
    
    except Exception as e:
        console.print(f"❌ File scanning error: {str(e)}", style="red")
        return False
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def test_organization_flow():
    """Test the complete organization flow with a small set of files."""
    console.print("\n[bold blue]Testing organization flow...[/bold blue]")
    
    # Create a temporary test directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Create some test files
        test_files = [
            ("document.txt", "This is an important document containing project specifications."),
            ("notes.md", "# Meeting Notes\nDiscussion points from yesterday's meeting."),
            ("script.py", "def hello():\n    print('Hello, world!')\n\nhello()")
        ]
        
        for filename, content in test_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        console.print(f"Created test directory at: {temp_dir}")
        console.print(f"Added {len(test_files)} test files")
        
        # Initialize components
        config = {
            'openai_api_key': os.getenv("OPENAI_API_KEY"),
            'model_name': os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        }
        scanner = DirectoryScanner()
        indexer = FileIndexer(config)
        organizer = FileOrganizer()
        
        # Scan directory
        console.print("Scanning directory...")
        files_metadata = scanner.scan_directory(temp_dir, recursive=True)
        
        if not files_metadata:
            console.print("❌ No files found in test directory", style="red")
            return False
        
        # Analyze files
        console.print("Analyzing files...")
        analysis_results = indexer.analyze_files(files_metadata)
        
        if not analysis_results:
            console.print("❌ File analysis failed", style="red")
            return False
        
        # Generate organization plan
        console.print("Generating organization plan...")
        organization_plan = organizer.generate_plan(analysis_results)
        
        if not organization_plan or not organization_plan.get('moves'):
            console.print("❌ Organization plan generation failed", style="red")
            return False
        
        # Display the plan
        console.print("Organization plan generated:")
        for move in organization_plan['moves']:
            source = Path(move['source']).name
            dest_folder = Path(move['destination']).parent.name
            console.print(f"  - {source} → {dest_folder}/")
        
        console.print("✅ Organization flow test successful", style="green")
        return True
        
    except Exception as e:
        console.print(f"❌ Organization flow error: {str(e)}", style="red")
        return False
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def run_tests():
    """Run all tests."""
    console.print("[bold]Running comprehensive tests for LLM Directory Organizer[/bold]")
    
    tests = [
        ("Environment setup", test_environment),
        ("Direct API connection", test_direct_api),
        ("LlamaIndex integration", test_llama_index),
        ("File scanning", test_file_scanning),
        ("Organization flow", test_organization_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        console.print(f"\n[bold cyan]Running test: {test_name}[/bold cyan]")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            console.print(f"❌ Unexpected error in {test_name}: {str(e)}", style="red")
            results.append((test_name, False))
    
    # Print summary
    console.print("\n[bold]Test Summary:[/bold]")
    failed_tests = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        style = "green" if success else "red"
        console.print(f"{status} - {test_name}", style=style)
        if not success:
            failed_tests += 1
    
    if failed_tests == 0:
        console.print("\n[bold green]All tests passed successfully![/bold green]")
        return 0
    else:
        console.print(f"\n[bold red]{failed_tests} test(s) failed.[/bold red]")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests()) 