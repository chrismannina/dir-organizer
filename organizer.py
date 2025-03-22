import os
import json
import shutil
import webbrowser
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.table import Table
from datetime import datetime

console = Console()

class FileOrganizer:
    """Handles file organization and TOC generation."""
    
    def __init__(self):
        self.base_dir = None
    
    def generate_plan(self, analysis_results: List[Dict]) -> Dict:
        """
        Generate an organization plan based on analysis results.
        
        Args:
            analysis_results (List[Dict]): List of file analysis results
            
        Returns:
            Dict: Organization plan containing file moves and renames
        """
        plan = {
            'moves': [],
            'folders': set(),
            'toc_entries': []
        }
        
        for result in analysis_results:
            original_path = Path(result['path'])
            
            if not self.base_dir:
                self.base_dir = original_path.parent
            
            # Create folder path
            folder_name = self._sanitize_folder_name(result['suggested_folder'])
            new_folder = self.base_dir / folder_name
            plan['folders'].add(str(new_folder))
            
            # Generate new file path
            new_path = new_folder / original_path.name
            
            # Add move operation
            plan['moves'].append({
                'source': str(original_path),
                'destination': str(new_path),
                'description': result['description'],
                'tags': result['tags']
            })
            
            # Add TOC entry
            plan['toc_entries'].append({
                'original_path': str(original_path),
                'new_path': str(new_path),
                'description': result['description'],
                'tags': result['tags']
            })
        
        return plan
    
    def display_plan(self, plan: Dict) -> str:
        """
        Display the organization plan in a formatted table.
        
        Returns:
            str: Path to the HTML report
        """
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Original Location")
        table.add_column("New Location")
        table.add_column("Description")
        table.add_column("Tags")
        
        for move in plan['moves']:
            table.add_row(
                str(Path(move['source']).relative_to(self.base_dir)),
                str(Path(move['destination']).relative_to(self.base_dir)),
                move['description'][:50] + "..." if len(move['description']) > 50 else move['description'],
                ", ".join(move['tags'])
            )
        
        console.print(table)
        
        # Generate HTML report for easier readability
        report_path = self.generate_html_report(plan)
        console.print(f"\n📊 Detailed report available at: {report_path}", style="blue")
        console.print(f"   Open in browser with: file://{os.path.abspath(report_path)}")
        
        return report_path
    
    def generate_html_report(self, plan: Dict) -> str:
        """
        Generate an HTML report of the proposed changes.
        
        Args:
            plan (Dict): Organization plan
            
        Returns:
            str: Path to the generated HTML file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.base_dir / f'organization_plan_{timestamp}.html'
        
        # Prepare the HTML content
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Directory Organization Plan</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding:.2rem;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .header {{
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 5px;
                    margin-bottom: 2rem;
                    border-left: 5px solid #6c5ce7;
                }}
                .summary {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 1rem;
                    margin-bottom: 2rem;
                }}
                .summary-item {{
                    flex: 1;
                    min-width: 200px;
                    background-color: #f1f2f6;
                    padding: 1rem;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 2rem;
                    box-shadow: 0 2px 15px rgba(0,0,0,0.1);
                }}
                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #6c5ce7;
                    color: white;
                    position: sticky;
                    top: 0;
                }}
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                tr:hover {{
                    background-color: #f1f2f6;
                }}
                .tag {{
                    display: inline-block;
                    background-color: #e2e8f0;
                    color: #4a5568;
                    padding: 2px 8px;
                    margin: 2px;
                    border-radius: 12px;
                    font-size: 0.85em;
                }}
                .folders {{
                    background-color: #f1f2f6;
                    padding: 1rem;
                    border-radius: 5px;
                    margin-bottom: 2rem;
                }}
                .footer {{
                    text-align: center;
                    font-size: 0.9em;
                    color: #718096;
                    margin-top: 3rem;
                    padding-top: 1rem;
                    border-top: 1px solid #e2e8f0;
                }}
                @media print {{
                    th {{
                        background-color: #ddd !important;
                        color: black !important;
                    }}
                    .tag {{
                        border: 1px solid #ccc;
                    }}
                    table {{
                        box-shadow: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Directory Organization Plan</h1>
                <p>Generated on {date} for {directory}</p>
            </div>
            
            <div class="summary">
                <div class="summary-item">
                    <h3>Files to Organize</h3>
                    <p style="font-size: 24px; font-weight: bold;">{file_count}</p>
                </div>
                <div class="summary-item">
                    <h3>New Folders</h3>
                    <p style="font-size: 24px; font-weight: bold;">{folder_count}</p>
                </div>
            </div>
            
            <h2>New Folder Structure</h2>
            <div class="folders">
                <ul>
                    {folder_list}
                </ul>
            </div>
            
            <h2>File Organization Plan</h2>
            <table>
                <thead>
                    <tr>
                        <th>Original Location</th>
                        <th>New Location</th>
                        <th>Description</th>
                        <th>Tags</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            
            <div class="footer">
                <p>Generated by LLM Directory Organizer</p>
            </div>
        </body>
        </html>
        """
        
        # Generate table rows
        table_rows = ""
        for move in plan['moves']:
            source_rel = str(Path(move['source']).relative_to(self.base_dir))
            dest_rel = str(Path(move['destination']).relative_to(self.base_dir))
            
            # Generate tags with HTML styling
            tags_html = ""
            for tag in move['tags']:
                tags_html += f'<span class="tag">{tag}</span> '
            
            # Add row
            table_rows += f"""
            <tr>
                <td>{source_rel}</td>
                <td>{dest_rel}</td>
                <td>{move['description']}</td>
                <td>{tags_html}</td>
            </tr>
            """
        
        # Generate folder list
        folder_list = ""
        for folder in sorted(plan['folders']):
            folder_rel = str(Path(folder).relative_to(self.base_dir))
            folder_list += f"<li>{folder_rel}</li>\n"
        
        # Fill in template values
        html_content = html_content.format(
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            directory=str(self.base_dir),
            file_count=len(plan['moves']),
            folder_count=len(plan['folders']),
            folder_list=folder_list,
            table_rows=table_rows
        )
        
        # Write the HTML file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
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
        for folder in plan['folders']:
            folder_path = Path(folder)
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                operations.append({
                    'type': 'create_folder',
                    'path': str(folder_path)
                })
        
        # Move files
        for move in plan['moves']:
            source = Path(move['source'])
            destination = Path(move['destination'])
            
            if source.exists():
                # Create parent directory if it doesn't exist
                destination.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                shutil.move(str(source), str(destination))
                operations.append({
                    'type': 'move',
                    'source': str(source),
                    'destination': str(destination)
                })
        
        return operations
    
    def generate_toc(self, plan: Dict) -> str:
        """
        Generate and save the table of contents.
        
        Args:
            plan (Dict): Organization plan containing TOC entries
            
        Returns:
            str: Path to the generated TOC file
        """
        toc_path = self.base_dir / 'file_organization_toc.json'
        
        toc_data = {
            'organization_date': self._get_iso_date(),
            'base_directory': str(self.base_dir),
            'files': plan['toc_entries']
        }
        
        with open(toc_path, 'w', encoding='utf-8') as f:
            json.dump(toc_data, f, indent=2, ensure_ascii=False)
        
        return str(toc_path)
    
    def _sanitize_folder_name(self, name: str) -> str:
        """Sanitize folder name for filesystem compatibility."""
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Remove leading/trailing spaces and periods
        name = name.strip('. ')
        
        # Default name if empty
        if not name:
            name = 'other'
        
        return name
    
    def _get_iso_date(self) -> str:
        """Get current date in ISO format."""
        return datetime.now().isoformat() 