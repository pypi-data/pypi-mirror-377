"""
Core functionality for organizing files based on their types.
"""

import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileOrganizer:
    """
    A class for organizing files into categorized folders based on file extensions.
    
    Attributes:
        base_dir (Path): The base directory to organize files from.
        log_file (Path): Path to the log file for recording operations.
        file_types (Dict): Dictionary mapping file categories to their extensions.
    """
    
    def __init__(self, directory: str):
        """
        Initialize the FileOrganizer with a target directory.
        
        Args:
            directory (str): Path to the directory containing files to organize.
        """
        self.base_dir = Path(directory).resolve()
        if not self.base_dir.exists() or not self.base_dir.is_dir():
            raise ValueError(f"Directory does not exist: {self.base_dir}")
        
        self.log_file = self.base_dir / "fileorganizer_log.json"
        
        # Define file types and their extensions
        self.file_types = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff", ".webp"],
            "documents": [".doc", ".docx", ".pdf", ".txt", ".rtf", ".odt", ".md", ".csv", ".xls", ".xlsx", ".ppt", ".pptx"],
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
            "video": [".mp4", ".avi", ".mov", ".wmv", ".mkv", ".flv", ".webm", ".m4v"],
            "code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".php", ".rb", ".go", ".rs", ".ts", ".json", ".xml"],
            "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"]
        }
    
    def get_file_category(self, file_path: Path) -> str:
        """
        Determine the category of a file based on its extension.
        
        Args:
            file_path (Path): Path to the file.
            
        Returns:
            str: The category of the file.
        """
        extension = file_path.suffix.lower()
        
        for category, extensions in self.file_types.items():
            if extension in extensions:
                return category
                
        return "others"
    
    def _create_category_dirs(self) -> Dict[str, Path]:
        """
        Create category directories if they don't exist.
        
        Returns:
            Dict[str, Path]: A dictionary mapping category names to directory paths.
        """
        category_dirs = {}
        
        # Add 'others' category for uncategorized files
        all_categories = list(self.file_types.keys()) + ["others"]
        
        for category in all_categories:
            category_dir = self.base_dir / category
            if not category_dir.exists():
                category_dir.mkdir(exist_ok=True)
                logger.info(f"Created directory: {category_dir}")
            
            category_dirs[category] = category_dir
            
        return category_dirs
    
    def _get_unique_path(self, target_path: Path) -> Path:
        """
        Generate a unique path if a file with the same name already exists.
        
        Args:
            target_path (Path): The target path to check.
            
        Returns:
            Path: A unique path with a suffix if necessary.
        """
        if not target_path.exists():
            return target_path
            
        base = target_path.stem
        extension = target_path.suffix
        directory = target_path.parent
        counter = 1
        
        while True:
            new_path = directory / f"{base}_{counter}{extension}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _move_file(self, source: Path, target_dir: Path) -> Tuple[Path, Path]:
        """
        Move a file to a target directory, handling duplicate filenames.
        
        Args:
            source (Path): Path to the source file.
            target_dir (Path): Path to the target directory.
            
        Returns:
            Tuple[Path, Path]: A tuple containing (source_path, target_path).
        """
        target_path = target_dir / source.name
        unique_target_path = self._get_unique_path(target_path)
        
        try:
            shutil.move(str(source), str(unique_target_path))
            logger.info(f"Moved: {source} -> {unique_target_path}")
            return source, unique_target_path
        except (PermissionError, OSError) as e:
            logger.error(f"Error moving file {source}: {e}")
            raise
    
    def organize(self) -> List[Tuple[Path, Path]]:
        """
        Organize files in the base directory into categorized subfolders.
        
        Returns:
            List[Tuple[Path, Path]]: A list of tuples containing (source_path, target_path) for each moved file.
        """
        import json
        
        category_dirs = self._create_category_dirs()
        moved_files = []
        
        # Get all files in the base directory (not in subdirectories)
        files = [f for f in self.base_dir.iterdir() if f.is_file() and f.name != "fileorganizer_log.json"]
        
        for file_path in files:
            category = self.get_file_category(file_path)
            target_dir = category_dirs[category]
            
            # Don't move files that are already in the correct category folder
            if file_path.parent == target_dir:
                continue
                
            try:
                source, target = self._move_file(file_path, target_dir)
                moved_files.append((source, target))
            except Exception as e:
                logger.error(f"Failed to move {file_path}: {e}")
                
        # Log the operations
        if moved_files:
            log_data = {
                "timestamp": time.time(),
                "operations": [
                    {"source": str(source), "target": str(target)} 
                    for source, target in moved_files
                ]
            }
            
            # Load existing log if it exists
            if self.log_file.exists():
                try:
                    with open(self.log_file, 'r') as f:
                        existing_data = json.load(f)
                    
                    # If it's a list, append our new data
                    if isinstance(existing_data, list):
                        existing_data.append(log_data)
                        log_data = existing_data
                    else:
                        # If it's a dict (old format), convert to list
                        log_data = [existing_data, log_data]
                except json.JSONDecodeError:
                    # If the file is corrupted, start fresh with just this operation
                    log_data = [log_data]
            else:
                # If no existing log, wrap in a list
                log_data = [log_data]
            
            # Write the updated log
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
            logger.info(f"Organized {len(moved_files)} files")
        else:
            logger.info("No files to organize")
            
        return moved_files
    
    def undo_last_operation(self) -> Optional[List[Tuple[Path, Path]]]:
        """
        Undo the last organize operation using the log file.
        
        Returns:
            Optional[List[Tuple[Path, Path]]]: A list of tuples containing (source_path, target_path)
                                             for each undone move, or None if there's nothing to undo.
        """
        import json
        
        if not self.log_file.exists():
            logger.warning("No log file found. Nothing to undo.")
            return None
            
        try:
            with open(self.log_file, 'r') as f:
                log_data = json.load(f)
                
            # Ensure we're working with a list
            if not isinstance(log_data, list):
                log_data = [log_data]
                
            if not log_data:
                logger.warning("Log file is empty. Nothing to undo.")
                return None
                
            # Get the last operation
            last_operation = log_data.pop()
            undone_files = []
            
            for move in last_operation["operations"]:
                source = Path(move["source"])
                current = Path(move["target"])
                
                if not current.exists():
                    logger.warning(f"File {current} doesn't exist anymore, cannot undo.")
                    continue
                    
                # Ensure the target directory exists
                if not source.parent.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                
                # Check for name conflicts and resolve
                unique_source = self._get_unique_path(source)
                
                try:
                    shutil.move(str(current), str(unique_source))
                    undone_files.append((current, unique_source))
                    logger.info(f"Undone move: {current} -> {unique_source}")
                except Exception as e:
                    logger.error(f"Failed to undo move {current} to {unique_source}: {e}")
            
            # Save the updated log
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
            logger.info(f"Undone {len(undone_files)} operations")
            return undone_files
        
        except json.JSONDecodeError:
            logger.error("Error reading log file. It might be corrupted.")
            return None
        except Exception as e:
            logger.error(f"Error undoing operations: {e}")
            return None