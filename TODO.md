# TODO List for LLM Directory Organizer

This document outlines planned improvements and features for the LLM Directory Organizer tool.

## High Priority

### Project Structure & Architecture
- [ ] Reorganize project structure into a proper Python package
  - [ ] Create a `src/llm_organizer` directory for source code
  - [ ] Move core modules into appropriate subpackages (core, utils, cli, etc.)
  - [ ] Implement proper package imports
- [ ] Implement configuration system
  - [ ] Replace direct .env usage with a robust config system (consider using Pydantic)
  - [ ] Support JSON/YAML config files with schema validation
  - [ ] Add ability to specify configuration profiles

### Core Functionality
- [ ] Improve organization logic quality
  - [ ] Implement consistent naming scheme options (camel, snake, pascal case)
  - [ ] Enhance folder suggestion by analyzing all files together before organizing
  - [ ] Implement two-pass analysis: first gather all metadata, then determine organization
- [ ] Respect project boundaries
  - [ ] Detect and preserve git repositories
  - [ ] Identify project directories (npm, python, etc.) and prevent internal reorganization
  - [ ] Add option to move entire project directories instead of reorganizing them internally
- [ ] Support hierarchical organization
  - [ ] Allow nested folder structures for better organization
  - [ ] Generate folder hierarchies based on tag relationships

### Data Management
- [ ] Implement caching and persistence system
  - [ ] Create a lightweight database for storing file analyses (SQLite)
  - [ ] Cache API responses to reduce API calls and costs
  - [ ] Store file metadata, tags, descriptions for faster reorganization
  - [ ] Track file history and changes over time

## Medium Priority

### Testing
- [ ] Improve test coverage
  - [ ] Implement proper unit tests for all components
  - [ ] Add integration tests for key workflows
  - [ ] Set up test fixtures and mocks to avoid API calls during testing
- [ ] Add CI/CD pipeline
  - [ ] Configure GitHub Actions for automated testing
  - [ ] Add linting and code quality checks
  - [ ] Implement automated releases

### User Experience
- [ ] Enhance usability
  - [ ] Make preview mode the default (require flag to disable)
  - [ ] Improve error messages and recovery options
  - [ ] Add a "dry run" option that shows file operations without HTML report
- [ ] Improve reporting capabilities
  - [ ] Add text-based summary reports
  - [ ] Support exporting reports in multiple formats (HTML, JSON, CSV)
  - [ ] Create a searchable interface for exploration of results

## Low Priority

### Packaging & Distribution
- [ ] Package for easy distribution
  - [ ] Create proper PyPI package
  - [ ] Add installation via pip
  - [ ] Support platform-specific installation methods (brew, apt, etc.)
- [ ] Create documentation
  - [ ] Generate API documentation
  - [ ] Provide detailed user guide
  - [ ] Create examples and tutorials

### Future Enhancements
- [ ] Develop GUI version
  - [ ] Implement web-based interface
  - [ ] Consider Electron app for desktop
  - [ ] Support for drag-and-drop operations
- [ ] Add advanced features
  - [ ] Support for image and media files (using vision models)
  - [ ] Duplicate file detection and handling
  - [ ] Integration with cloud storage (Google Drive, Dropbox, etc.)
  - [ ] Scheduled organization tasks

## Immediate Tasks

1. Implement improved organization logic with consistent naming
2. Add detection of project boundaries (git repos, etc.)
3. Create basic unit tests for critical components
4. Implement simple SQLite database for caching analysis results
5. Make preview mode the default option 