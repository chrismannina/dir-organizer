import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class OperationLogger:
    """Handles logging of file operations and undo functionality."""
    
    def __init__(self):
        self.log_dir = Path.home() / '.file_organizer' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_operations(self, operations: List[Dict]):
        """
        Log file operations to a JSON file.
        
        Args:
            operations (List[Dict]): List of operations to log
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f'operations_{timestamp}.json'
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'operations': operations
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def get_last_operations(self) -> Optional[List[Dict]]:
        """
        Get the most recent set of operations.
        
        Returns:
            Optional[List[Dict]]: List of operations or None if no logs found
        """
        try:
            # Get the most recent log file
            log_files = sorted(self.log_dir.glob('operations_*.json'))
            if not log_files:
                return None
            
            latest_log = log_files[-1]
            
            # Read the operations
            with open(latest_log, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            return log_data['operations']
            
        except Exception as e:
            print(f"Error reading operations log: {str(e)}")
            return None
    
    def undo_operations(self, operations: List[Dict]):
        """
        Undo a set of file operations.
        
        Args:
            operations (List[Dict]): List of operations to undo
        """
        # Reverse the operations to undo them in the correct order
        for operation in reversed(operations):
            try:
                if operation['type'] == 'move':
                    source = Path(operation['source'])
                    destination = Path(operation['destination'])
                    
                    if destination.exists():
                        # Create parent directory if it doesn't exist
                        source.parent.mkdir(parents=True, exist_ok=True)
                        # Move the file back
                        shutil.move(str(destination), str(source))
                
                elif operation['type'] == 'create_folder':
                    folder_path = Path(operation['path'])
                    # Only remove if empty
                    try:
                        folder_path.rmdir()
                    except OSError:
                        # Folder not empty, skip
                        pass
                        
            except Exception as e:
                print(f"Error undoing operation {operation}: {str(e)}")
                continue 