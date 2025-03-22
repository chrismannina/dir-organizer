#!/bin/bash
# Installation script for LLM Directory Organizer

set -e  # Exit on error

echo "Installing LLM Directory Organizer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3.8 or newer."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
python_min_version="3.8"

if [ "$(printf '%s\n' "$python_min_version" "$python_version" | sort -V | head -n1)" != "$python_min_version" ]; then
    echo "Python $python_min_version or newer is required. You have Python $python_version."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install the package
echo "Installing dependencies and package..."
pip install --upgrade pip
pip install -e .

echo ""
echo "Installation complete! You can now use LLM Directory Organizer."
echo ""
echo "To get started:"
echo "1. Set your OpenAI API key in a .env file or as an environment variable:"
echo "   export OPENAI_API_KEY=\"your-api-key-here\""
echo ""
echo "2. Run the organizer:"
echo "   llm-organizer organize /path/to/directory"
echo ""
echo "For more options, run:"
echo "   llm-organizer --help"
echo ""
