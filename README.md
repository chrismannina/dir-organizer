# LLM Directory Organizer

An AI-powered tool that organizes your directories using large language models.

## Features

- **AI-Powered Organization**: Uses GPT models to understand file content and suggest organization
- **Interactive Preview**: Preview changes before applying them
- **HTML Reports**: Generate beautiful reports of proposed organization
- **Undo Functionality**: Easily revert any changes
- **API Testing**: Built-in tools to verify API connectivity
- **Hidden App Folder**: Stores all generated files in a hidden `.llm_organizer` folder
- **Smart Image Handling**: Extracts and uses EXIF metadata from images for better organization
- **File Migration**: Command to migrate organizer-generated files to the hidden folder

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-directory-organizer.git
cd llm-directory-organizer

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Requirements

- Python 3.8+
- OpenAI API key

## Usage

### Set up your API key

```bash
# Set your OpenAI API key as an environment variable
export OPENAI_API_KEY="your-api-key-here"

# Or create a .env file in the project root
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Basic Commands

```bash
# Organize a directory
llm-organizer organize /path/to/directory

# Preview changes without applying them
llm-organizer organize /path/to/directory --preview

# Undo the last organization operation
llm-organizer undo

# Test API connection
llm-organizer test-api

# Migrate organizer files to the hidden .llm_organizer folder
llm-organizer migrate /path/to/directory
```

### Advanced Options

```bash
# Organize without recursively scanning subdirectories
llm-organizer organize /path/to/directory --no-recursive

# Exclude specific patterns (can be used multiple times)
llm-organizer organize /path/to/directory --exclude "*.log" --exclude "temp*"

# Use a YAML file with exclusion patterns
llm-organizer organize /path/to/directory --exclude-file exclusions.yaml

# Automatically open HTML report in browser
llm-organizer organize /path/to/directory --open-report
```

## Project Structure

```
llm-directory-organizer/
├── src/
│   └── llm_organizer/           # Main package
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # CLI entry point
│       ├── cli/                 # Command line interface modules
│       ├── config/              # Configuration schema and loaders
│       ├── core/                # Core functionality
│       │   ├── scanner.py       # Directory scanning
│       │   ├── indexer.py       # File analysis with LLM
│       │   └── organizer.py     # File organization logic
│       ├── models/              # Data models
│       └── utils/               # Utility modules
│           └── logger.py        # Operation logging
├── tests/                       # Unit tests
├── pyproject.toml               # Project metadata
├── setup.py                     # Installation script
└── README.md                    # This file
```

## Configuration

The application can be configured through:

1. Environment variables
2. YAML configuration files
3. Command line arguments

You can create a custom configuration file at `~/.config/llm-organizer/config.yaml`:

```yaml
llm:
  api_key: "your-api-key-here"
  model_name: "gpt-3.5-turbo"
  max_tokens: 1000
  temperature: 0.2

scanner:
  text_extensions: [".txt", ".md", ".py", ".js", ".html", ".css"]
  max_file_size_mb: 5
  exclude_patterns: ["*.log", "temp*"]
  exclude_hidden: true

organizer:
  naming_scheme: "camelCase"
  max_folder_depth: 3
  preserve_projects: true
  project_markers: [".git", "package.json", "pyproject.toml"]
```

## License

MIT License
