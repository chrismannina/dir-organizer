# LLM Directory Organizer: Program Flow

```mermaid
flowchart TD
    %% Main program flow
    Start([Start Program]) --> ParseArgs[Parse Command Line Arguments]
    ParseArgs --> CheckAction{Check Action}
    
    %% Organize flow
    CheckAction -->|Organize| ScanDir[Scan Directory]
    ScanDir --> ExtractMeta[Extract File Metadata]
    ExtractMeta --> ExtractContent[Extract Content from Text Files]
    ExtractContent --> LLMAnalysis[LLM Analysis]
    
    %% LLM Analysis subgraph
    subgraph "LLM Analysis Phase"
        LLMAnalysis --> IndexFiles[Index Files with LlamaIndex]
        IndexFiles --> QueryLLM[Query LLM for Analysis]
        QueryLLM --> GenerateTags[Generate Tags]
        QueryLLM --> SuggestFolder[Suggest Folder Placement]
        QueryLLM --> CreateDesc[Create File Description]
        GenerateTags & SuggestFolder & CreateDesc --> CompileResults[Compile Analysis Results]
    end
    
    %% Organization Planning
    CompileResults --> OrgPlan[Generate Organization Plan]
    OrgPlan --> DetermineTargets[Determine Target Folders]
    DetermineTargets --> CreateFolderPlan[Create Folder Structure Plan]
    CreateFolderPlan --> MapFiles[Map Files to Destinations]
    
    %% Preview and Confirmation
    MapFiles --> IsPreview{Preview Mode?}
    IsPreview -->|Yes| DisplayPreview[Display Organization Preview]
    DisplayPreview --> AskConfirm{Ask for Confirmation}
    IsPreview -->|No| AskConfirm
    
    %% User decision
    AskConfirm -->|Confirmed| ExecutePlan[Execute Organization Plan]
    AskConfirm -->|Cancelled| Exit([Exit Program])
    
    %% Execution Phase
    ExecutePlan --> CreateFolders[Create New Folders]
    CreateFolders --> MoveFiles[Move Files to New Locations]
    MoveFiles --> LogOps[Log All Operations]
    
    %% Documentation Phase
    LogOps --> GenerateTOC[Generate Table of Contents]
    GenerateTOC --> SaveTOC[Save Master Reference File]
    SaveTOC --> DisplayComplete[Display Completion Message]
    DisplayComplete --> Exit
    
    %% Undo flow
    CheckAction -->|Undo| GetLastOps[Get Last Operations]
    GetLastOps --> AskUndoConfirm{Confirm Undo?}
    AskUndoConfirm -->|Yes| UndoOps[Undo Operations]
    AskUndoConfirm -->|No| Exit
    UndoOps --> DisplayUndoComplete[Display Undo Complete]
    DisplayUndoComplete --> Exit
    
    %% Styling
    classDef phase fill:#f9f,stroke:#333,stroke-width:2px;
    classDef decision fill:#bbf,stroke:#333,stroke-width:2px;
    classDef action fill:#dfd,stroke:#333,stroke-width:1px;
    classDef io fill:#ffd,stroke:#333,stroke-width:1px;
    
    class ScanDir,ExtractMeta,ExtractContent phase;
    class LLMAnalysis,OrgPlan,ExecutePlan,GenerateTOC phase;
    class CheckAction,IsPreview,AskConfirm,AskUndoConfirm decision;
    class ParseArgs,IndexFiles,QueryLLM,GenerateTags,SuggestFolder,CreateDesc action;
    class CompileResults,DetermineTargets,CreateFolderPlan,MapFiles action;
    class CreateFolders,MoveFiles,LogOps,SaveTOC,UndoOps action;
    class DisplayPreview,DisplayComplete,DisplayUndoComplete io;
```

## Component Descriptions

### 1. Command Parsing
- Parses command line arguments to determine the action (organize or undo)
- Sets options like recursive scanning and preview mode

### 2. Directory Scanning Phase
- Scans target directory recursively or non-recursively
- Extracts metadata from all files (name, size, type, dates)
- Extracts content from compatible text-based files

### 3. LLM Analysis Phase
- Uses LlamaIndex to index file content and metadata
- Queries the LLM to:
  - Generate relevant tags for each file
  - Suggest appropriate folder placement
  - Create a brief description of the file's content
- Compiles all analysis results into a structured dataset

### 4. Organization Planning Phase
- Generates a comprehensive organization plan
- Determines which folders need to be created
- Maps each file to its destination folder

### 5. Preview & Confirmation Phase
- Displays the proposed organization changes to the user
- Shows before/after file structure
- Asks for confirmation before proceeding

### 6. Execution Phase
- Creates new folders according to the plan
- Moves files to their designated locations
- Logs all operations for potential rollback

### 7. Documentation Phase
- Generates a master table of contents
- Records original locations, new locations, and file descriptions
- Saves information as a reference file

### 8. Undo Functionality
- Retrieves the log of the last organization operation
- Confirms with the user before proceeding
- Reverts all file moves by moving files back to original locations
- Removes empty folders that were created 