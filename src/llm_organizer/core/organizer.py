"""File organization module."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from rich.console import Console

console = Console()


class FileOrganizer:
    """Handles file organization and TOC generation."""

    def __init__(self, config=None):
        self.base_dir = None
        self.config = config
        self.folder_naming_scheme = "snake_case"
        self.categories_naming_scheme = "pascal_case"
        self.preserve_projects = True
        self.project_markers = [
            ".git",
            "package.json",
            "pyproject.toml",
            "Cargo.toml",
            "Makefile",
        ]

        # Set naming schemes from config if provided
        if config and hasattr(config, "organizer"):
            self.folder_naming_scheme = config.organizer.naming_scheme
            self.categories_naming_scheme = config.organizer.categories_naming_scheme
            self.preserve_projects = config.organizer.preserve_projects
            self.project_markers = config.organizer.project_markers

    def generate_intelligent_schema(self, analysis_results: List[Dict]) -> Dict:
        """
        Generate an intelligent organization schema based on all files together.

        This method sends all file metadata, tags, and descriptions to the LLM
        to create a cohesive organization plan with categories and subcategories.

        Args:
            analysis_results (List[Dict]): List of all file analysis results

        Returns:
            Dict: Organization schema with folder hierarchy and file mappings
        """
        # Prepare a consolidated view of all files for the LLM
        files_summary = []
        for result in analysis_results:
            files_summary.append(
                {
                    "filename": Path(result["path"]).name,
                    "tags": result["tags"],
                    "description": result["description"],
                    "category": result.get("category", "Other"),
                    "current_path": str(
                        Path(result["path"]).relative_to(self.base_dir)
                    ),
                }
            )

        # Prepare prompt for the LLM - expanded to include category information
        prompt = f"""
You are an expert file organizer. Given the following list of files with their tags, descriptions, and categories,
create a logical folder structure that groups related files together.

Consider the following guidelines:
1. Create main categories based on file types, topics, or project areas
2. Create appropriate subcategories where relevant
3. Use descriptive, clear folder names (don't worry about formatting - just use spaces and readable names)
4. Consider hierarchical relationships between files
5. Maximum folder depth should be 3 levels (including the base directory)
6. Group files by interest areas and themes, not just file types
7. Create general purpose folders that can accommodate multiple related files
8. Use the category field as a starting point, but feel free to create more appropriate organization
9. Pay special attention to media files like images, videos, and audio - try to keep them organized by content rather than just file type
10. Avoid using "Other" as a folder name unless absolutely necessary - try to find meaningful groupings
11. For images, consider grouping them by theme, subject matter, or purpose rather than putting all in a generic "Images" folder

Here are the files to organize:
{json.dumps(files_summary, indent=2)}

Return your answer as a JSON object with the following structure:
{{
  "folder_hierarchy": [
    {{
      "name": "Folder Name",
      "path": "Folder Name",
      "parent": null,
      "children": [
        {{
          "name": "Subfolder Name",
          "path": "Folder Name/Subfolder Name",
          "parent": "Folder Name",
          "children": []
        }}
      ]
    }}
  ],
  "file_mappings": {{
    "original/path/to/file.txt": "Folder Name/Subfolder Name"
  }}
}}

Note: Don't worry about the formatting style of folder names (like camelCase or snake_case) - just use clear, descriptive names.
The formatting will be handled automatically by the system based on user preferences.
"""

        try:
            # Import here to avoid circular imports
            from openai import OpenAI

            from llm_organizer.config.defaults import load_config

            config = load_config()
            api_key = config.llm.api_key

            # Use GPT-4o specifically for organization planning
            organization_model = config.llm.organization_model

            console.print(
                f"\n🧠 Using {organization_model} for intelligent organization planning..."
            )

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=organization_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert file organizer that outputs valid JSON. Your goal is to create logical folder structures based on file content, tags, and categories.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )

            # Extract the JSON content from the response
            response_content = response.choices[0].message.content
            schema = json.loads(response_content)

            # Ensure basic structure exists for safety
            if "folder_hierarchy" not in schema:
                schema["folder_hierarchy"] = []
            if "file_mappings" not in schema:
                schema["file_mappings"] = {}

            # If no file mappings were created, add fallback logic to assign files to folders
            if not schema["file_mappings"] and schema["folder_hierarchy"]:
                # Assign files based on tags and folder names
                self._assign_files_to_folders(schema, files_summary)

            # Save the schema for future reference
            self._save_schema(schema)

            return schema

        except Exception as e:
            console.print(f"Error generating intelligent schema: {str(e)}", style="red")
            # Fallback to a basic schema if the API call fails
            return self._generate_fallback_schema(analysis_results)

    def _save_schema(self, schema: Dict) -> None:
        """Save the organization schema to a file for future reference."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        app_data_dir = self._get_app_data_folder()
        schema_path = app_data_dir / f"organization_schema_{timestamp}.json"

        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        console.print(f"\n💾 Organization schema saved to: {schema_path}", style="blue")

    def _generate_fallback_schema(self, analysis_results: List[Dict]) -> Dict:
        """Generate a basic schema when the API call fails."""
        # Create a dictionary to group files by their primary tag
        tag_groups = {}
        for result in analysis_results:
            if result["tags"]:
                primary_tag = result["tags"][
                    0
                ].title()  # Use the first tag as primary category
                if primary_tag not in tag_groups:
                    tag_groups[primary_tag] = []

                rel_path = str(Path(result["path"]).relative_to(self.base_dir))
                tag_groups[primary_tag].append(rel_path)

        # Generate a folder hierarchy and file mappings
        schema = {"folder_hierarchy": [], "file_mappings": {}}

        # Add folders to hierarchy
        for folder_name in tag_groups.keys():
            schema["folder_hierarchy"].append(
                {
                    "name": folder_name,
                    "path": folder_name,
                    "parent": None,
                    "children": [],
                }
            )

            # Map files to this folder
            for file_path in tag_groups[folder_name]:
                schema["file_mappings"][file_path] = folder_name

        return schema

    def _assign_files_to_folders(self, schema: Dict, files_summary: List[Dict]) -> None:
        """
        Assign files to appropriate folders when LLM doesn't provide mappings.

        Args:
            schema: The folder schema with hierarchy but no mappings
            files_summary: The list of file metadata
        """
        # Extract all available folder paths
        available_folders = []

        def extract_paths(folders):
            for folder in folders:
                available_folders.append(folder["path"])
                if folder["children"]:
                    extract_paths(folder["children"])

        extract_paths(schema["folder_hierarchy"])

        from llm_organizer.utils import format_naming_scheme

        # Format the "Other" folder name according to the naming scheme
        other_folder_name = format_naming_scheme("Other", self.folder_naming_scheme)

        # Add "Other" as a fallback folder if it doesn't exist
        if (
            other_folder_name not in available_folders
            and "Other" not in available_folders
        ):
            schema["folder_hierarchy"].append(
                {
                    "name": other_folder_name,
                    "path": other_folder_name,
                    "parent": None,
                    "children": [],
                }
            )
            available_folders.append(other_folder_name)

        # Add "Images" folder if it doesn't exist
        images_folder_name = format_naming_scheme("Images", self.folder_naming_scheme)
        if (
            images_folder_name not in available_folders
            and "Images" not in available_folders
        ):
            image_files_exist = any(
                file_info.get("category", "").lower() == "images"
                for file_info in files_summary
            )
            if image_files_exist:
                schema["folder_hierarchy"].append(
                    {
                        "name": images_folder_name,
                        "path": images_folder_name,
                        "parent": None,
                        "children": [],
                    }
                )
                available_folders.append(images_folder_name)

        # For each file, find the most appropriate folder
        for file_info in files_summary:
            best_folder = None
            best_score = -1

            # Convert tags to lowercase for comparison
            file_tags = [tag.lower() for tag in file_info["tags"]]
            filename_lower = file_info["filename"].lower()
            category = file_info.get("category", "").lower()

            # Special case for images
            image_extensions = [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".svg",
                ".webp",
            ]
            is_image = any(filename_lower.endswith(ext) for ext in image_extensions)

            if (
                is_image
                and category == "images"
                and images_folder_name in available_folders
            ):
                schema["file_mappings"][file_info["current_path"]] = images_folder_name
                continue

            for folder_path in available_folders:
                folder_parts = folder_path.lower().split("/")
                score = 0

                # Special case for matching category to folder name
                if category and any(
                    part.lower() == category.lower() for part in folder_parts
                ):
                    score += 5  # Higher score for direct category match

                # Check if any folder part matches file tags
                for part in folder_parts:
                    # Score based on folder name matching tags
                    for tag in file_tags:
                        if part in tag or tag in part:
                            score += 2

                    # Score based on folder name appearing in description
                    if (
                        "description" in file_info
                        and part in file_info["description"].lower()
                    ):
                        score += 1

                    # Score based on folder name appearing in filename
                    if part in filename_lower:
                        score += 3

                if score > best_score:
                    best_score = score
                    best_folder = folder_path

            # Assign file to the best matching folder, or formatted "Other" if no match
            if best_score > 0:
                schema["file_mappings"][file_info["current_path"]] = best_folder
            else:
                schema["file_mappings"][file_info["current_path"]] = other_folder_name

    def _process_intelligent_schema(
        self, schema: Dict, analysis_results: List[Dict]
    ) -> Dict:
        """
        Process the intelligent schema to generate a plan.

        Args:
            schema (Dict): The intelligent organization schema
            analysis_results (List[Dict]): Original analysis results

        Returns:
            Dict: Organization plan with moves, folders, and TOC entries
        """
        plan = {"moves": [], "folders": set(), "toc_entries": [], "skipped_files": []}

        # Apply naming scheme to folder paths in schema
        from llm_organizer.utils import format_naming_scheme

        # Create a mapping of original paths to formatted paths
        formatted_paths = {}

        # Format folder paths in hierarchy
        def format_paths(folders):
            for folder in folders:
                # Format each part of the path
                path_parts = folder["path"].split("/")
                formatted_parts = [
                    format_naming_scheme(part, self.folder_naming_scheme)
                    for part in path_parts
                ]
                formatted_path = "/".join(formatted_parts)

                # Update the folder object
                formatted_paths[folder["path"]] = formatted_path
                folder["formatted_path"] = formatted_path

                # Process children recursively
                if folder["children"]:
                    format_paths(folder["children"])

        # Format all paths in the hierarchy
        format_paths(schema["folder_hierarchy"])

        # Update file mappings to use formatted paths
        formatted_mappings = {}
        for file_path, folder_path in schema["file_mappings"].items():
            formatted_folder = formatted_paths.get(folder_path, folder_path)
            formatted_mappings[file_path] = formatted_folder

        schema["file_mappings"] = formatted_mappings

        # Create all folders from the hierarchy
        self._process_folder_hierarchy(
            schema["folder_hierarchy"], plan["folders"], use_formatted=True
        )

        # Format the "Other" folder name according to the naming scheme
        other_folder_formatted = format_naming_scheme(
            "Other", self.folder_naming_scheme
        )

        # Ensure the "Other" folder exists if any files will be mapped there
        other_folder_needed = False
        for result in analysis_results:
            original_path = Path(result["path"])
            rel_path = str(original_path.relative_to(self.base_dir))

            # Check if any file will go to "Other" or "other"
            dest_folder = schema["file_mappings"].get(rel_path, other_folder_formatted)
            if (
                dest_folder.lower() == "other"
                or dest_folder.lower() == other_folder_formatted.lower()
            ):
                other_folder_needed = True
                # Update the mapping to use the properly formatted name
                schema["file_mappings"][rel_path] = other_folder_formatted
                break

        if other_folder_needed:
            other_folder = self.base_dir / other_folder_formatted
            plan["folders"].add(str(other_folder))

        # Special handling for image files
        image_folder_formatted = format_naming_scheme(
            "Images", self.folder_naming_scheme
        )
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"]

        # Create an images folder if needed
        images_folder_needed = False

        # Map each file to its destination
        for result in analysis_results:
            original_path = Path(result["path"])
            rel_path = str(original_path.relative_to(self.base_dir))

            # Skip files in project directories
            if self.preserve_projects and self._is_in_project_directory(original_path):
                plan["skipped_files"].append(
                    {"path": str(original_path), "reason": "In project directory"}
                )
                console.print(
                    f"Skipping {original_path.name} (in project directory)",
                    style="yellow",
                )
                continue

            # Get destination folder from schema mapping or use default
            dest_folder = schema["file_mappings"].get(rel_path, other_folder_formatted)

            # Apply special handling for image files
            if original_path.suffix.lower() in image_extensions:
                # Check category from analysis results
                if (
                    result.get("category", "").lower() == "images"
                    and dest_folder.lower() == other_folder_formatted.lower()
                ):
                    dest_folder = image_folder_formatted
                    images_folder_needed = True

            # Create full paths
            new_folder = self.base_dir / dest_folder
            new_path = new_folder / original_path.name

            # Add move operation
            plan["moves"].append(
                {
                    "source": str(original_path),
                    "destination": str(new_path),
                    "description": result["description"],
                    "tags": result["tags"],
                }
            )

            # Add TOC entry
            plan["toc_entries"].append(
                {
                    "original_path": str(original_path),
                    "new_path": str(new_path),
                    "description": result["description"],
                    "tags": result["tags"],
                }
            )

        # Add images folder if needed
        if images_folder_needed:
            images_folder = self.base_dir / image_folder_formatted
            plan["folders"].add(str(images_folder))

        return plan

    def _is_in_project_directory(self, file_path: Path) -> bool:
        """
        Check if a file is within a project directory.

        Args:
            file_path (Path): Path to the file to check

        Returns:
            bool: True if the file is in a project directory, False otherwise
        """
        if not self.preserve_projects:
            return False

        # Check all parent directories up to the base directory
        current_dir = file_path.parent
        base_dir = self.base_dir

        while current_dir != base_dir and current_dir.is_relative_to(base_dir):
            # Check for project markers
            for marker in self.project_markers:
                marker_path = current_dir / marker
                if marker_path.exists():
                    return True

            # Move up one directory
            current_dir = current_dir.parent

        # Check the base directory itself
        for marker in self.project_markers:
            marker_path = base_dir / marker
            if marker_path.exists():
                return True

        return False

    def _process_folder_hierarchy(
        self, hierarchy: List[Dict], folder_set: set, use_formatted: bool = False
    ) -> None:
        """
        Process the folder hierarchy and add all paths to the folder set.

        Args:
            hierarchy (List[Dict]): List of folder hierarchy nodes
            folder_set (set): Set to populate with folder paths
            use_formatted (bool): Whether to use formatted paths from the schema
        """
        for folder in hierarchy:
            # Add this folder to the set
            if use_formatted and "formatted_path" in folder:
                folder_path = self.base_dir / folder["formatted_path"]
            else:
                folder_path = self.base_dir / folder["path"]

            folder_set.add(str(folder_path))

            # Process children recursively
            if folder["children"]:
                self._process_folder_hierarchy(
                    folder["children"], folder_set, use_formatted
                )

    def generate_plan(
        self, analysis_results: List[Dict], use_intelligent_schema: bool = False
    ) -> Dict:
        """
        Generate an organization plan based on analysis results.

        Args:
            analysis_results (List[Dict]): List of file analysis results
            use_intelligent_schema (bool): Whether to use the intelligent schema approach

        Returns:
            Dict: Organization plan containing file moves and renames
        """
        # Ensure base_dir is set
        if analysis_results and not self.base_dir:
            self.base_dir = Path(analysis_results[0]["path"]).parent

        plan = {"moves": [], "folders": set(), "toc_entries": [], "skipped_files": []}

        # Filter out files in project directories if project preservation is enabled
        filtered_results = []
        for result in analysis_results:
            file_path = Path(result["path"])
            if self.preserve_projects and self._is_in_project_directory(file_path):
                plan["skipped_files"].append(
                    {"path": str(file_path), "reason": "In project directory"}
                )
                console.print(
                    f"Skipping {file_path.name} (in project directory)", style="yellow"
                )
            else:
                filtered_results.append(result)

        # If all files were skipped, return empty plan
        if not filtered_results:
            console.print(
                "All files are in project directories and will be preserved.",
                style="yellow",
            )
            return plan

        # Use the new intelligent schema if requested
        if use_intelligent_schema:
            schema = self.generate_intelligent_schema(filtered_results)
            return self._process_intelligent_schema(schema, filtered_results)

        # Original implementation - process files individually
        else:
            for result in filtered_results:
                original_path = Path(result["path"])

                # Create folder path
                folder_name = self._sanitize_folder_name(result["suggested_folder"])
                new_folder = self.base_dir / folder_name
                plan["folders"].add(str(new_folder))

                # Generate new file path
                new_path = new_folder / original_path.name

                # Add move operation
                plan["moves"].append(
                    {
                        "source": str(original_path),
                        "destination": str(new_path),
                        "description": result["description"],
                        "tags": result["tags"],
                    }
                )

                # Add TOC entry
                plan["toc_entries"].append(
                    {
                        "original_path": str(original_path),
                        "new_path": str(new_path),
                        "description": result["description"],
                        "tags": result["tags"],
                    }
                )

        return plan

    def display_plan(self, plan: Dict) -> str:
        """
        Display the organization plan and generate an HTML report.

        Args:
            plan (Dict): Organization plan containing file moves

        Returns:
            str: Path to the generated HTML file
        """
        # Count files in each destination
        dest_counts = {}
        for move in plan["moves"]:
            dest_folder = os.path.dirname(move["destination"])
            dest_counts[dest_folder] = dest_counts.get(dest_folder, 0) + 1

        # Display folder structure
        console.print("\n📂 Folder Structure:", style="bold blue")
        for folder in sorted(plan["folders"]):
            rel_path = os.path.relpath(folder, self.base_dir)
            if rel_path == ".":
                continue  # Skip base directory
            file_count = dest_counts.get(folder, 0)
            file_str = "files" if file_count != 1 else "file"
            console.print(f"  📁 {rel_path} ({file_count} {file_str})")

        # Display file moves
        console.print(f"\n🔄 Files to Move: {len(plan['moves'])}", style="bold blue")

        # Display skipped files if any
        if "skipped_files" in plan and plan["skipped_files"]:
            console.print(
                f"\n⏭️ Files Skipped: {len(plan['skipped_files'])}", style="bold yellow"
            )
            for skipped in plan["skipped_files"][
                :5
            ]:  # Show only first 5 to avoid clutter
                rel_path = os.path.relpath(skipped["path"], self.base_dir)
                console.print(f"  • {rel_path} ({skipped['reason']})", style="yellow")
            if len(plan["skipped_files"]) > 5:
                console.print(
                    f"    ... and {len(plan['skipped_files']) - 5} more files",
                    style="yellow",
                )

        # Show only a few moves to keep the output manageable
        for i, move in enumerate(plan["moves"][:5]):
            source_rel = os.path.relpath(move["source"], self.base_dir)
            dest_rel = os.path.relpath(move["destination"], self.base_dir)
            console.print(f"  • {source_rel} → {dest_rel}")

        if len(plan["moves"]) > 5:
            console.print(f"    ... and {len(plan['moves']) - 5} more files")

        # Generate HTML report
        return self.generate_html_report(plan)

    def generate_html_report(self, plan: Dict) -> str:
        """
        Generate an HTML report of the proposed changes.

        Args:
            plan (Dict): Organization plan

        Returns:
            str: Path to the generated HTML file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        app_data_dir = self._get_app_data_folder()
        report_path = app_data_dir / f"organization_plan_{timestamp}.html"

        # Count files in each folder
        folder_counts = {}
        for move in plan["moves"]:
            dest_folder = os.path.dirname(move["destination"])
            folder_counts[dest_folder] = folder_counts.get(dest_folder, 0) + 1

        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Organization Plan</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .folder {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #4CAF50;
                    padding: 10px 15px;
                    margin-bottom: 10px;
                    border-radius: 4px;
                }}
                .file {{
                    background-color: #fff;
                    border: 1px solid #ddd;
                    padding: 10px 15px;
                    margin-bottom: 5px;
                    border-radius: 4px;
                    display: flex;
                    justify-content: space-between;
                }}
                .file:hover {{
                    background-color: #f5f5f5;
                }}
                .file-description {{
                    flex: 1;
                    margin-right: 15px;
                }}
                .file-tags {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 5px;
                    align-items: center;
                }}
                .tag {{
                    background-color: #e1f5fe;
                    border-radius: 12px;
                    padding: 3px 10px;
                    font-size: 0.8em;
                    white-space: nowrap;
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .move {{
                    display: flex;
                    gap: 10px;
                    align-items: center;
                }}
                .arrow {{
                    color: #2196F3;
                    font-weight: bold;
                }}
                .stats {{
                    background-color: #e8f5e9;
                    padding: 10px 15px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }}
                .skipped {{
                    background-color: #fff3e0;
                    border-left: 4px solid #ff9800;
                    padding: 10px 15px;
                    margin-bottom: 10px;
                    border-radius: 4px;
                }}
                .reason {{
                    color: #e65100;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <h1>File Organization Plan</h1>
            <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

            <div class="stats">
                <h3>Statistics</h3>
                <p>Total files to move: {len(plan["moves"])}</p>
                <p>Total folders to create: {len(plan["folders"])}</p>
                {f'<p>Total files skipped: {len(plan["skipped_files"])}</p>' if "skipped_files" in plan and plan["skipped_files"] else ''}
            </div>

            <div class="section">
                <h2>Folder Structure</h2>
                {self._generate_folder_section_html(plan["folders"], folder_counts)}
            </div>

            <div class="section">
                <h2>File Moves</h2>
                {self._generate_moves_section_html(plan["moves"])}
            </div>

            {"<div class='section'><h2>Skipped Files</h2>" + self._generate_skipped_section_html(plan.get("skipped_files", [])) + "</div>" if "skipped_files" in plan and plan["skipped_files"] else ""}
        </body>
        </html>
        """

        # Save the HTML file
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        console.print(f"\n📊 Detailed report saved to: {report_path}", style="blue")
        console.print(f"   Open in browser with: file://{os.path.abspath(report_path)}")

        return str(report_path)

    def _generate_folder_section_html(self, folders, folder_counts):
        """Generate HTML for the folder structure section."""
        folders_html = ""
        for folder in sorted(folders):
            rel_path = os.path.relpath(folder, self.base_dir)
            if rel_path == ".":
                continue  # Skip base directory
            file_count = folder_counts.get(folder, 0)
            file_str = "files" if file_count != 1 else "file"
            folders_html += f"""
            <div class="folder">
                <b>{rel_path}</b> ({file_count} {file_str})
            </div>
            """
        return folders_html

    def _generate_moves_section_html(self, moves):
        """Generate HTML for the file moves section."""
        moves_html = ""
        for move in moves:
            source_rel = os.path.relpath(move["source"], self.base_dir)
            dest_rel = os.path.relpath(move["destination"], self.base_dir)
            tags_html = "".join(
                [f'<span class="tag">{tag}</span>' for tag in move["tags"]]
            )
            moves_html += f"""
            <div class="file">
                <div class="file-description">
                    <div class="move">
                        <div>{source_rel}</div>
                        <div class="arrow">→</div>
                        <div>{dest_rel}</div>
                    </div>
                    <div>{move["description"]}</div>
                </div>
                <div class="file-tags">
                    {tags_html}
                </div>
            </div>
            """
        return moves_html

    def _generate_skipped_section_html(self, skipped_files):
        """Generate HTML for the skipped files section."""
        if not skipped_files:
            return "<p>No files were skipped.</p>"

        skipped_html = ""
        for skipped in skipped_files:
            rel_path = os.path.relpath(skipped["path"], self.base_dir)
            skipped_html += f"""
            <div class="skipped">
                <div>{rel_path}</div>
                <div class="reason">Reason: {skipped["reason"]}</div>
            </div>
            """
        return skipped_html

    def execute_plan(self, plan: Dict) -> List[Dict]:
        """
        Execute the organization plan.

        Args:
            plan (Dict): Organization plan to execute

        Returns:
            List[Dict]: List of executed operations for logging
        """
        operations = []

        # Create folders
        for folder in plan["folders"]:
            folder_path = Path(folder)
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                operations.append({"type": "create_folder", "path": str(folder_path)})

        # Move files
        for move in plan["moves"]:
            source = Path(move["source"])
            destination = Path(move["destination"])

            if source.exists():
                # Create parent directory if it doesn't exis
                destination.parent.mkdir(parents=True, exist_ok=True)

                # Move the file
                shutil.move(str(source), str(destination))
                operations.append(
                    {
                        "type": "move",
                        "source": str(source),
                        "destination": str(destination),
                    }
                )

        return operations

    def generate_toc(self, plan: Dict) -> str:
        """
        Generate and save the table of contents.

        Args:
            plan (Dict): Organization plan containing TOC entries

        Returns:
            str: Path to the generated TOC file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        app_data_dir = self._get_app_data_folder()
        toc_path = app_data_dir / f"file_organization_toc_{timestamp}.json"

        toc_data = {
            "organization_date": self._get_iso_date(),
            "base_directory": str(self.base_dir),
            "files": plan["toc_entries"],
        }

        with open(toc_path, "w", encoding="utf-8") as f:
            json.dump(toc_data, f, indent=2, ensure_ascii=False)

        return str(toc_path)

    def _sanitize_folder_name(self, name: str) -> str:
        """Sanitize folder name for filesystem compatibility."""
        # Format the name according to the naming scheme
        from llm_organizer.utils import format_naming_scheme

        # First apply the naming scheme formatting
        name = format_naming_scheme(name, self.folder_naming_scheme)

        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, "_")

        # Remove leading/trailing spaces and periods
        name = name.strip(". ")

        # Default name if empty
        if not name:
            name = format_naming_scheme("other", self.folder_naming_scheme)

        return name

    def _get_iso_date(self) -> str:
        """Get current date in ISO format."""
        return datetime.now().isoformat()

    def _get_app_data_folder(self) -> Path:
        """Get or create the application data folder within the base directory."""
        app_data_dir = self.base_dir / ".llm_organizer"

        # Create the folder if it doesn't exist
        if not app_data_dir.exists():
            app_data_dir.mkdir(exist_ok=True)

        return app_data_dir

    def migrate_organizer_files(self) -> Dict:
        """
        Migrate existing organizer-generated files to the app data folder.

        Returns:
            Dict: A summary of the migration process
        """
        if not self.base_dir:
            console.print("Base directory not set. Cannot migrate files.", style="red")
            return {"success": False, "message": "Base directory not set"}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        app_data_dir = self._get_app_data_folder()

        # File patterns to search for and migrate
        patterns = [
            "organization_plan_*.html",
            "organization_schema_*.json",
            "file_organization_toc_*.json",
        ]

        migration_summary = {
            "success": True,
            "message": "Migration completed successfully",
            "migrated_files": [],
            "errors": [],
        }

        # Search for files in base directory and migrate them
        for pattern in patterns:
            for file_path in self.base_dir.glob(pattern):
                # Skip if the file is already in the app data folder
                if app_data_dir in file_path.parents:
                    continue

                try:
                    # Create new path in app data folder
                    new_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
                    new_path = app_data_dir / new_name

                    # Move the file
                    shutil.move(str(file_path), str(new_path))
                    migration_summary["migrated_files"].append(
                        {"original": str(file_path), "new": str(new_path)}
                    )
                    console.print(
                        f"Migrated: {file_path.name} -> {new_path.name}", style="green"
                    )
                except Exception as e:
                    migration_summary["errors"].append(
                        {"file": str(file_path), "error": str(e)}
                    )
                    console.print(
                        f"Error migrating {file_path.name}: {str(e)}", style="red"
                    )

        # Update summary message
        if (
            len(migration_summary["migrated_files"]) == 0
            and len(migration_summary["errors"]) == 0
        ):
            migration_summary["message"] = "No files found to migrate"
        elif len(migration_summary["errors"]) > 0:
            migration_summary["success"] = False
            migration_summary["message"] = (
                f"Migration completed with {len(migration_summary['errors'])} errors"
            )

        console.print(
            f"\n📁 Migration summary: {migration_summary['message']}", style="blue"
        )
        return migration_summary
