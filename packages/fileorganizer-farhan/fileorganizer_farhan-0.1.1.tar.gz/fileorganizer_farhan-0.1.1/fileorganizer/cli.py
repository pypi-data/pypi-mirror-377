"""
Command Line Interface (CLI) for FileOrganizer.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional
from .organizer import FileOrganizer

logger = logging.getLogger(__name__)

def setup_parser() -> argparse.ArgumentParser:
    """
    Set up command line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="fileorganizer",
        description="Organize files in a directory into categorized subfolders."
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Organize command
    organize_parser = subparsers.add_parser("organize", help="Organize files in a directory")
    organize_parser.add_argument("folder", help="Folder path to organize")
    organize_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    # Undo command
    undo_parser = subparsers.add_parser("undo", help="Undo the last organize operation")
    undo_parser.add_argument("folder", help="Folder where the operation was performed")
    undo_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    return parser

def run_organize(args: argparse.Namespace) -> int:
    """
    Run the organize command.
    
    Args:
        args (argparse.Namespace): Command line arguments.
        
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    try:
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            
        folder_path = Path(args.folder).resolve()
        if not folder_path.exists() or not folder_path.is_dir():
            logger.error(f"Directory does not exist: {folder_path}")
            return 1
            
        organizer = FileOrganizer(str(folder_path))
        moved_files = organizer.organize()
        
        print(f"Organized {len(moved_files)} files")
        if moved_files and args.verbose:
            for source, target in moved_files:
                print(f"Moved: {source.name} -> {target}")
                
        return 0
        
    except Exception as e:
        logger.error(f"Error organizing files: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def run_undo(args: argparse.Namespace) -> int:
    """
    Run the undo command.
    
    Args:
        args (argparse.Namespace): Command line arguments.
        
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    try:
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            
        folder_path = Path(args.folder).resolve()
        if not folder_path.exists() or not folder_path.is_dir():
            logger.error(f"Directory does not exist: {folder_path}")
            return 1
            
        organizer = FileOrganizer(str(folder_path))
        undone_files = organizer.undo_last_operation()
        
        if undone_files is None:
            print("Nothing to undo")
            return 0
            
        print(f"Undone {len(undone_files)} operations")
        if undone_files and args.verbose:
            for source, target in undone_files:
                print(f"Moved back: {source.name} -> {target}")
                
        return 0
        
    except Exception as e:
        logger.error(f"Error undoing operations: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args (Optional[List[str]]): Command line arguments.
        
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    parser = setup_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 0
        
    if parsed_args.command == "organize":
        return run_organize(parsed_args)
    elif parsed_args.command == "undo":
        return run_undo(parsed_args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())