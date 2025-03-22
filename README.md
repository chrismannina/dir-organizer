# LLM-Powered Directory Organizer

## What is it?

The **LLM-Powered Directory Organizer** is your AI-powered file organization assistant. It looks at your messy directories, understands what each file is about, and automatically sorts everything into a logical folder structure. Think of it as having a personal librarian who reads, categorizes, and shelves all your digital files intelligently.

## How does it work?

**In simple terms:** The tool scans your files, uses AI to understand what each file contains and what it's for, then organizes them into appropriate folders. It shows you the plan before making any changes, and keeps track of everything so you can undo if needed.

**In more detail:**

1. **Finding your files:** The tool examines every file in your chosen directory (and subfolders if you want). It collects basic information like file names, types, sizes, and when they were created or modified.

2. **Understanding your content:** For text-based files (documents, code, etc.), the tool reads the content to better understand what they're about. For PDFs and Word documents, it extracts the text to analyze.

3. **AI analysis:** The AI looks at each file and determines:
   - What topics or categories best describe it
   - Which folder it should go in
   - A brief summary of what the file contains

4. **Showing you the plan:** Before moving anything, the tool displays a clear preview of:
   - Which files will go where
   - What folders will be created
   - Brief descriptions of each file
   You can review this plan and decide whether to proceed.

5. **Organizing your files:** When you approve, the tool:
   - Creates the necessary folders
   - Moves each file to its new home
   - Keeps the original file names (no renaming by default)

6. **Creating a directory guide:** The tool creates a master reference file that records:
   - Where each file was originally
   - Where it was moved to
   - What the file contains (according to the AI)
   This helps you find everything later.

7. **Safety net:** Every change is logged, and you can easily undo the entire organization with a single command if you're not happy with the results.

## Why use this tool?

- **Save time:** Let AI handle the tedious work of sorting through hundreds or thousands of files
- **Discover forgotten files:** Uncover and categorize files you may have forgotten about
- **Organize intelligently:** Files are grouped by their actual content and purpose, not just names or dates
- **Play it safe:** Preview changes before they happen and easily undo if needed
- **Find things later:** The master reference file helps you locate anything quickly

## Usage Examples

### Basic Organization

Organize all files in a directory:

```bash
python main.py organize ~/Documents/messy_folder
```

### Preview Mode

See what changes would be made without actually moving files:

```bash
python main.py organize ~/Downloads --preview
```

### Non-Recursive Mode

Only organize files in the main directory, ignoring subfolders:

```bash
python main.py organize ~/Desktop --no-recursive
```

### Exclude Specific Directories or File Patterns

Exclude specific directories or file patterns:

```bash
python main.py organize ~/Documents/folder_to_organize --exclude "*.log" --exclude "temp/*"
```

### Use a File with Exclusion Patterns

Use a file with exclusion patterns:

```bash
python main.py organize ~/Documents/folder_to_organize --exclude-file exclusions.yaml
```

### Combine Multiple Options

Combine multiple options:

```bash
python main.py organize ~/Desktop --no-recursive --exclude "*.tmp" --preview
```

### Generate and Open HTML Report

Generate and automatically open an HTML report of the organization plan:

```bash
python main.py organize ~/Documents/folder_to_organize --preview --open-report
```

### Undoing Changes

If you're not happy with how things were organized:

```bash
python main.py undo
```

## What's happening behind the scenes?

When you run the organizer, the following process takes place:

1. **Scanning Phase:**
   - The scanner module walks through your directory structure
   - It reads file metadata (size, date, type) for every file
   - For text files (including PDFs and Word docs), it extracts content for analysis
   - This builds a complete inventory of all your files

2. **AI Analysis Phase:**
   - Each file's information is processed by an AI language model
   - The AI examines the file's name, metadata, and content
   - It determines the most appropriate categories and folder placement
   - It generates a brief description of what the file contains
   - All of this happens through the LlamaIndex integration

3. **Planning Phase:**
   - The organizer creates a structured plan for file arrangement
   - It determines which folders need to be created
   - It maps each file to its destination folder
   - It prepares entries for the master reference document

4. **Confirmation Phase:**
   - You're shown a complete preview of the proposed changes
   - The preview includes original locations, new locations, and descriptions
   - You can choose to proceed or cancel at this point

5. **Execution Phase:**
   - New folders are created as needed
   - Files are moved to their designated locations
   - Each operation is logged for potential rollback
   - The master table of contents is generated and saved

6. **Safety Mechanisms:**
   - All operations are recorded in a detailed log
   - The undo feature reads this log and can reverse all changes
   - No files are deleted in the process, only moved

This approach combines the intelligence of AI with careful file handling to ensure your data is organized effectively while remaining safe and recoverable.

## Core Features

- **Smart Scanning:**  
  The tool examines all your files, including those hidden in subfolders, and collects important information about them.

- **AI-Powered Analysis:**  
  Using advanced AI technology, the tool understands what your files are about and how they should be organized.

- **Automatic Organization:**  
  Creates an intelligent folder structure and moves your files where they belong, without changing their names.

- **Complete File Catalog:**  
  Generates a searchable index of all your files with descriptions so you can easily find anything later.

- **User-Friendly Interface:**  
  Simple commands let you specify which folders to organize, preview changes before committing, and undo if needed.

- **Safe Operations:**  
  Every action is recorded, and you can reverse everything with a single command if you're not satisfied.

## Getting Started

### 1. Installation

**Prerequisites:**
- Python 3.8 or higher
- pip (Python package manager)

**Step 1: Get the software**
```bash
git clone https://github.com/yourusername/llm-directory-organizer.git
cd llm-directory-organizer
```

**Step 2: Set up a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Step 3: Install required packages**
```bash
pip install -r requirements.txt
```

**Step 4: Set up your API key**
Copy `.env.example` to `.env` and add your OpenAI API key:
```bash
cp .env.example .env
# Then edit the .env file with your favorite editor
```

### 2. Quick Start

**Organize a directory with all default settings:**
```bash
python main.py organize ~/Documents/folder_to_organize
```

**Preview what changes would be made without actually moving files:**
```bash
python main.py organize ~/Documents/folder_to_organize --preview
```

**Exclude specific directories or file patterns:**
```bash
python main.py organize ~/Documents/folder_to_organize --exclude "*.log" --exclude "temp/*"
```

**Use a file with exclusion patterns:**
```bash
python main.py organize ~/Documents/folder_to_organize --exclude-file exclusions.yaml
```

**Combine multiple options:**
```bash
python main.py organize ~/Desktop --no-recursive --exclude "*.tmp" --preview
```

**Generate and open HTML report:**
```bash
python main.py organize ~/Documents/folder_to_organize --preview --open-report
```

**Undo the last organization operation:**
```bash
python main.py undo
```

## Command Line Options

```
python main.py organize DIRECTORY [OPTIONS]
```

Options:
- `--recursive/--no-recursive`: Include subdirectories (enabled by default)
- `--preview/--no-preview`: Show changes before execution (enabled by default)
- `--exclude, -e`: Patterns of files or directories to exclude (can be used multiple times)
- `--exclude-file`: YAML file containing exclusion patterns to load
- `--open-report/--no-open-report`: Automatically open the HTML report in browser (disabled by default)

## Tips for Better Results

1. **Start with small directories**: For your first run, try a folder with fewer files to get familiar with the process.

2. **Always use preview mode first**: This helps you see what the AI is suggesting before making any changes.

3. **Exclude system directories**: Use `--exclude` to skip directories like `node_modules`, `venv`, `.git`, etc. The tool automatically excludes some common system directories.

4. **Use HTML reports for better readability**: Use the `--open-report` option to review changes in a well-formatted HTML document, which is easier to read than terminal output.

5. **Use the exclusion file**: For complex organization tasks, create a custom exclusion file based on the provided `exclusions.yaml` template.

6. **Use pattern exclusions**: You can use wildcard patterns like `--exclude "*.log"` or `--exclude "temp/*"` to skip certain file types or directories.

7. **Clear API key access**: Make sure your OpenAI API key is properly configured in the `.env` file.

## Technical Details

For developers and advanced users interested in the inner workings or contributing to the project:

### Architecture & Components

- **main.py:**  
  The entry point with command-line interface logic.

- **scanner.py:**  
  Handles directory traversal and file metadata extraction.

- **indexer.py:**  
  Manages the AI integration for file analysis.

- **organizer.py:**  
  Implements the file organization logic.

- **logger.py:**  
  Manages operation logging and undo functionality.

### Dependencies

- **LlamaIndex:** For AI-powered understanding of file content
- **OpenAI API:** Provides the AI capabilities (requires an API key)
- **Python libraries:** Rich (for terminal UI), Click (for CLI), and others

## Future Plans

We're working on enhancing the tool with:

- **Faster processing:** Parallel file analysis for large directories
- **Memory features:** Remember previous analyses to speed up repeated runs
- **Custom rules:** Allow users to define their own organization preferences
- **GUI interface:** A graphical version for those who prefer not to use command lines
- **More file types:** Better support for image, audio, and video content

## Need Help?

If you encounter any issues:

1. Check the logs in your home directory under `.file_organizer/logs/`
2. Ensure your OpenAI API key is valid and has sufficient credits
3. For large directories, be patient as analysis may take some time
4. Use the `--preview` flag to troubleshoot without making changes
5. Submit an issue on our GitHub repository with details of the problem
