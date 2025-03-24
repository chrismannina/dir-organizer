# TODO List for LLM Directory Organizer

This document outlines planned improvements and features for the LLM Directory Organizer tool.

## Priority Definitions
- **P0**: Critical - Blocking issues that need immediate attention
- **P1**: High - Should be addressed in the next development cycle
- **P2**: Medium - Important but can wait until P1 items are addressed
- **P3**: Low - Nice-to-have features or enhancements for future development

## High Priority

### Project Structure & Architecture
- [x] **P1** Reorganize project structure into a proper Python package
  - [x] Create a `src/llm_organizer` directory for source code
  - [x] Move core modules into appropriate subpackages (core, utils, cli, etc.)
  - [x] Implement proper package imports
  - [x] Update import statements throughout codebase
  - [x] Ensure backwards compatibility or provide migration path

  *Notes: This should be done early as it affects all other development. Create a new branch for this work to avoid disrupting ongoing development.*

- [x] **P1** Implement configuration system
  - [x] Replace direct .env usage with a robust config system (using Pydantic)
  - [x] Support JSON/YAML config files with schema validation
  - [x] Add ability to specify configuration profiles (e.g., development, production)
  - [x] Create migration utility to convert existing .env files to new format
  - [x] Document configuration options and provide examples

  *Notes: This is foundational for many other features, particularly those requiring user customization.*

### Core Functionality
- [ ] **P0** Improve organization logic quality
  - [ ] Implement consistent naming scheme options (camel, snake, pascal case)
  - [ ] Enhance folder suggestion by analyzing all files together before organizing
  - [ ] Implement two-pass analysis: first gather all metadata, then determine organization
  - [ ] Create pluggable "organization strategy" system to allow different approaches
  - [ ] Add configuration options for controlling organization depth and granularity

  *Notes: This is the core value proposition of the tool and should be prioritized. The current implementation organizes files individually without considering the entire set.*

- [ ] **P0** Respect project boundaries
  - [ ] Detect and preserve git repositories (check for .git directory)
  - [ ] Identify project directories (look for package.json, pyproject.toml, etc.)
  - [ ] Prevent internal reorganization of recognized project directories
  - [ ] Add option to move entire project directories instead of reorganizing them internally
  - [ ] Implement safeguards to prevent breaking functional codebases

  *Notes: Critical to prevent breaking existing projects. Should be implemented before any other organization logic improvements.*

- [ ] **P1** Support hierarchical organization
  - [ ] Allow nested folder structures for better organization
  - [ ] Generate folder hierarchies based on tag relationships
  - [ ] Implement depth limits to prevent overly complex hierarchies
  - [ ] Add visualization of proposed hierarchy before execution

  *Notes: This builds on the improved organization logic and should be implemented after the two-pass analysis system.*

### Data Management
- [ ] **P1** Implement caching and persistence system
  - [ ] Create a lightweight database for storing file analyses (SQLite)
  - [ ] Design schema to efficiently store file metadata, tags, descriptions, and history
  - [ ] Cache API responses to reduce API calls and costs
  - [ ] Store file metadata, tags, descriptions for faster reorganization
  - [ ] Track file history and changes over time
  - [ ] Implement data pruning to prevent database bloat

  *Notes: This will significantly improve performance and reduce API costs. The database should be local to the user's machine with clear documentation on storage locations and privacy implications.*

## Medium Priority

### Testing
- [ ] **P1** Improve test coverage
  - [ ] Implement proper unit tests for all components
  - [ ] Add integration tests for key workflows
  - [ ] Set up test fixtures and mocks to avoid API calls during testing
  - [ ] Create benchmark tests to measure performance improvements
  - [ ] Implement regression tests for critical functionality

  *Notes: Critical for stability as the codebase grows. Start with unit tests for the core components (scanner, indexer, organizer).*

- [ ] **P2** Add CI/CD pipeline
  - [ ] Configure GitHub Actions for automated testing
  - [ ] Add linting and code quality checks
  - [ ] Implement automated releases
  - [ ] Set up dependency scanning and updates
  - [ ] Add code coverage reporting

  *Notes: This should be implemented after the project structure refactoring and test improvements.*

### User Experience
- [ ] **P1** Enhance usability
  - [ ] Make preview mode the default (require flag to disable)
  - [ ] Improve error messages and recovery options
  - [ ] Add a "dry run" option that shows file operations without HTML report
  - [ ] Implement progress bars for long-running operations
  - [ ] Add keyboard shortcuts for common operations

  *Notes: These changes will make the tool more user-friendly and safer to use. Start with making preview mode the default.*

- [ ] **P2** Improve reporting capabilities
  - [ ] Add text-based summary reports
  - [ ] Support exporting reports in multiple formats (HTML, JSON, CSV)
  - [ ] Create a searchable interface for exploration of results
  - [ ] Allow filtering reports by file type, size, or other criteria
  - [ ] Implement options to customize report appearance

  *Notes: Builds on existing HTML report functionality. Ensure that all report formats include the same information.*

### Error Handling and Logging
- [ ] **P1** Enhance error handling
  - [ ] Implement comprehensive error catching throughout the application
  - [ ] Create user-friendly error messages with suggestions for resolution
  - [ ] Add detailed logging with configurable verbosity levels
  - [ ] Implement crash recovery for interruptions during file operations
  - [ ] Add option to submit anonymized error reports

  *Notes: Critical for production usage. Should be implemented early to help during development.*

## Low Priority

### Packaging & Distribution
- [ ] **P2** Package for easy distribution
  - [ ] Create proper PyPI package
  - [ ] Add installation via pip
  - [ ] Support platform-specific installation methods (brew, apt, etc.)
  - [ ] Implement dependency management and version constraints
  - [ ] Create installation verification and troubleshooting tools

  *Notes: Important for wider adoption but requires stable core functionality first.*

- [ ] **P3** Create comprehensive documentation
  - [ ] Generate API documentation with Sphinx or similar tool
  - [ ] Provide detailed user guide with examples
  - [ ] Create tutorials for common use cases
  - [ ] Add documentation for extensibility and customization
  - [ ] Set up documentation hosting and versioning

  *Notes: Start with basic documentation early, then expand as features stabilize.*

### Performance Optimizations
- [ ] **P1** Implement concurrency for faster processing
  - [ ] Add async/await support for LLM API calls
  - [ ] Implement thread pool for parallel file analysis
  - [ ] Add progress tracking for concurrent operations
  - [ ] Include throttling to prevent API rate limiting
  - [ ] Ensure thread safety for shared resources

  *Notes: This is critical for performance as LLM API calls are the primary bottleneck. Implementing concurrency can drastically reduce processing time for large directories.*

- [ ] **P2** Optimize performance
  - [ ] Implement parallel processing for file analysis
  - [ ] Add batch processing for API calls to reduce overhead
  - [ ] Optimize file scanning and filtering for large directories
  - [ ] Implement memory usage optimizations for large files
  - [ ] Add performance benchmarks and monitoring

  *Notes: Important for handling large file collections, but dependent on core functionality stability.*

### Future Enhancements
- [ ] **P3** Develop GUI version
  - [ ] Implement web-based interface
  - [ ] Consider Electron app for desktop
  - [ ] Support for drag-and-drop operations
  - [ ] Add visual organization planning
  - [ ] Implement user accounts and settings synchronization (for web version)

  *Notes: Only start after CLI version is mature and stable. Consider as a separate project that builds on the core library.*

- [ ] **P3** Add advanced features
  - [ ] Support for image and media files (using vision models)
  - [ ] Implement duplicate file detection and handling
  - [ ] Add integration with cloud storage (Google Drive, Dropbox, etc.)
  - [ ] Support scheduled organization tasks
  - [ ] Implement content-based search across organized files

  *Notes: These features extend the core functionality and should be implemented incrementally after the basic functionality is stable.*

### Extensibility
- [ ] **P2** Create plugin system
  - [ ] Design and implement plugin architecture
  - [ ] Add extension points for custom file analyzers
  - [ ] Support custom organization strategies
  - [ ] Create hooks for pre/post organization actions
  - [ ] Develop documentation and examples for plugin developers

  *Notes: This allows the community to extend the tool's functionality without modifying the core code.*

## Immediate Tasks (Next 2 Weeks)

1. **P0** Implement project boundary detection (git repos, etc.)
   - First step to prevent breaking existing projects
   - Focus on detecting .git folders and common project files

2. **P0** Improve organization logic with consistent naming
   - Add naming scheme configuration options
   - Modify the folder suggestion logic to consider file relationships

3. **P1** Create basic unit tests for critical components
   - Set up testing framework
   - Implement tests for scanner and organizer modules

4. **P1** Make preview mode the default option
   - Update command line interface
   - Update documentation and examples

5. **P1** Enhance error handling and logging
   - Implement more robust error catching
   - Add detailed logging with configurable levels

## Roadmap: 3-Month Plan

### Month 1
- Complete all Immediate Tasks
- Implement basic caching for API responses
- Begin project structure reorganization

### Month 2
- Complete project structure reorganization
- Implement configuration system
- Add comprehensive test coverage for core components
- Begin implementing SQLite database for caching

### Month 3
- Complete SQLite implementation
- Add CI/CD pipeline
- Improve reporting capabilities
- Begin work on packaging for distribution

## High Priority
- [x] Update all imports in remaining modules to match new package structure
- [x] Move sample configuration files to the project
- [x] Create sample exclusions file templates
- [x] Make sure test suite is fully functional
- [ ] Add docstrings to all modules, classes and functions
- [x] Verify CLI commands work correctly with new structure

## Medium Priority
- [ ] Add type hints to all functions
- [ ] Improve error handling throughout the application
- [ ] Add more logging for better debugging
- [ ] Create user configuration wizard
- [ ] Add progress bars for long-running operations
- [ ] Implement better file content extraction for PDFs and other binary formats

## Low Priority
- [ ] Create a web interface
- [ ] Add support for more configuration formats
- [ ] Implement plugin system for custom file analysis
- [ ] Create a desktop GUI application
- [ ] Support for multiple organization presets
- [ ] Add file and folder tagging system

## Documentation
- [x] Complete API documentation
- [x] Write user guide with examples
- [ ] Create developer guide for contributors
- [ ] Add screenshots to README
- [x] Document configuration options


- [ ] Remove duplicate API tests at beginning of run "Testing API connection before analysis..."
- [ ] Need a better method to put exclusions
- [ ] Really need to fix the categorizations - and allow for sub directories. it should be a call to 4o or something to really organize everything
- [ ] Should be able to move files into the folders that already exist.
- [ ] we should really rethink all of this.
- [ ] should embed the file descriptions.
- [ ] index the files?
- [ ] can be used for an os search too
- [ ] make sure that if the folder contents is a repository, it can treat that repo as a file in the sense that we get a description of that whole folder. and that the inside cannot be organized by the application
- [ ] a lot of these flags on the cli are not needed... preview? should be like that by default.
- [ ] async or parallelization
- [ ] should maybe revert to just reading READMEs for git repos. and if the readme is non existent or too vague, we should likely start analyzing some of the files. not all. tags should include which programming langauge.
