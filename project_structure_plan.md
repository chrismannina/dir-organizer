# Project Structure Reorganization Plan

## Current Structure

The current project has a flat structure with all Python modules in the root directory:

```
.
├── .env
├── .env.example
├── .git/
├── .gitignore
├── LICENSE
├── README.md
├── __pycache__/
├── exclusions.yaml
├── indexer.py
├── logger.py
├── main.py
├── organizer.py
├── program_flow.md
├── requirements.txt
├── scanner.py
├── test_api.py
├── test_app.py
├── test_dir/
├── test_llama_index.py
└── TODO.md
```

## Target Structure

We'll reorganize into a proper Python package structure:

```
.
├── .git/
├── .gitignore
├── LICENSE
├── README.md
├── TODO.md
├── docs/
│   ├── program_flow.md
│   └── images/
├── examples/
│   └── basic_organization.py
├── pyproject.toml
├── requirements-dev.txt
├── requirements.txt
├── setup.py
├── src/
│   └── llm_organizer/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── commands.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── defaults.py
│       │   └── schema.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── indexer.py
│       │   ├── organizer.py
│       │   └── scanner.py
│       ├── data/
│       │   ├── __init__.py
│       │   └── exclusions.yaml
│       ├── models/
│       │   ├── __init__.py
│       │   └── file_metadata.py
│       └── utils/
│           ├── __init__.py
│           └── logger.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_core/
    │   ├── __init__.py
    │   ├── test_indexer.py
    │   ├── test_organizer.py
    │   └── test_scanner.py
    ├── test_e2e.py
    └── test_utils/
        ├── __init__.py
        └── test_logger.py
```

## Migration Steps

### 1. Create the Basic Package Structure

```bash
# Create directories
mkdir -p src/llm_organizer/{cli,config,core,data,models,utils} docs/images examples tests/{test_core,test_utils}

# Create __init__.py files
touch src/llm_organizer/__init__.py
touch src/llm_organizer/{cli,config,core,data,models,utils}/__init__.py
touch tests/__init__.py
touch tests/{test_core,test_utils}/__init__.py
```

### 2. Move Core Functionality

1. **Move scanner.py to core:**
   ```bash
   cp scanner.py src/llm_organizer/core/scanner.py
   ```

2. **Move indexer.py to core:**
   ```bash
   cp indexer.py src/llm_organizer/core/indexer.py
   ```

3. **Move organizer.py to core:**
   ```bash
   cp organizer.py src/llm_organizer/core/organizer.py
   ```

4. **Move logger.py to utils:**
   ```bash
   cp logger.py src/llm_organizer/utils/logger.py
   ```

5. **Move exclusions.yaml to data:**
   ```bash
   cp exclusions.yaml src/llm_organizer/data/exclusions.yaml
   ```

### 3. Create CLI Module

1. **Create __main__.py for direct execution:**
   - Extract the CLI functionality from main.py
   - Move it to src/llm_organizer/__main__.py

2. **Create cli/commands.py:**
   - Extract command implementations from main.py
   - Move them to src/llm_organizer/cli/commands.py

### 4. Create Config System

1. **Create config/schema.py:**
   - Define configuration schema classes using Pydantic
   - Include validation rules

2. **Create config/defaults.py:**
   - Define default configuration values
   - Include functions to load from environment or files

### 5. Create Models

1. **Create models/file_metadata.py:**
   - Define structured classes for file metadata
   - Use proper type hints

### 6. Create Setup Files

1. **Create pyproject.toml:**
   ```toml
   [build-system]
   requires = ["setuptools>=42", "wheel"]
   build-backend = "setuptools.build_meta"

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = "test_*.py"
   ```

2. **Create setup.py:**
   ```python
   from setuptools import setup, find_packages

   setup(
       name="llm_organizer",
       version="0.1.0",
       packages=find_packages(where="src"),
       package_dir={"": "src"},
       include_package_data=True,
       package_data={
           "llm_organizer": ["data/*.yaml"],
       },
       install_requires=[
           # Transfer dependencies from requirements.txt
       ],
       entry_points={
           "console_scripts": [
               "llm-organizer=llm_organizer.__main__:main",
           ],
       },
   )
   ```

### 7. Migrate Tests

1. **Create conftest.py:**
   - Define pytest fixtures and configuration

2. **Move test_app.py to tests/test_e2e.py:**
   - Adapt imports to use the new package structure

3. **Create individual test files:**
   - Split test functionality by module

### 8. Update Imports

After moving files, we need to update all import statements to use the new package structure:

1. From relative imports:
   ```python
   from scanner import DirectoryScanner
   ```

2. To package imports:
   ```python
   from llm_organizer.core.scanner import DirectoryScanner
   ```

3. Update all modules to use the new import paths

### 9. Documentation

1. **Move program_flow.md to docs/:**
   ```bash
   cp program_flow.md docs/program_flow.md
   ```

2. **Create examples/basic_organization.py:**
   - Showcase basic usage of the package

### 10. Split Requirements

1. **Update requirements.txt:**
   - Keep production dependencies

2. **Create requirements-dev.txt:**
   - Add development dependencies like pytest

## Testing the Migration

After restructuring, follow these steps to ensure everything works:

1. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

2. **Run tests:**
   ```bash
   pytest
   ```

3. **Verify the CLI works:**
   ```bash
   python -m llm_organizer organize test_dir --preview
   ```

## Backwards Compatibility

To maintain backward compatibility during the transition:

1. **Create wrapper scripts:**
   - Keep main.py in the root but have it import from the package

2. **Deprecation notices:**
   - Add deprecation warnings when old scripts are used directly

## Implementation Timeline

1. **Day 1:** Create directory structure and setup files
2. **Day 2-3:** Move core modules and update imports
3. **Day 4:** Set up CLI system
4. **Day 5:** Create configuration system
5. **Day 6:** Migrate tests and ensure they pass
6. **Day 7:** Add documentation and examples
