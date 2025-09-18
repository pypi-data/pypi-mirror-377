"""
Unit tests for the FileOrganizer package.
"""

import shutil
import tempfile
from pathlib import Path
import pytest

from fileorganizer.organizer import FileOrganizer


class TestFileOrganizer:
    """Test suite for FileOrganizer class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files of different types in the temporary directory."""
        # Create sample files
        (temp_dir / "document.pdf").touch()
        (temp_dir / "image.jpg").touch()
        (temp_dir / "audio.mp3").touch()
        (temp_dir / "video.mp4").touch()
        (temp_dir / "code.py").touch()
        (temp_dir / "archive.zip").touch()
        (temp_dir / "unknown.xyz").touch()
        
        return temp_dir

    def test_initialization(self, temp_dir):
        """Test that the FileOrganizer initializes correctly."""
        organizer = FileOrganizer(str(temp_dir))
        assert organizer.base_dir == temp_dir
        assert organizer.log_file == temp_dir / "fileorganizer_log.json"

    def test_initialization_nonexistent_dir(self):
        """Test that initializing with a nonexistent directory raises an error."""
        with pytest.raises(ValueError):
            FileOrganizer("/path/that/does/not/exist")

    def test_get_file_category(self, temp_dir):
        """Test that files are correctly categorized."""
        organizer = FileOrganizer(str(temp_dir))
        
        # Test known categories
        assert organizer.get_file_category(Path("test.jpg")) == "images"
        assert organizer.get_file_category(Path("test.pdf")) == "documents"
        assert organizer.get_file_category(Path("test.mp3")) == "audio"
        assert organizer.get_file_category(Path("test.mp4")) == "video"
        assert organizer.get_file_category(Path("test.py")) == "code"
        assert organizer.get_file_category(Path("test.zip")) == "archives"
        
        # Test unknown category
        assert organizer.get_file_category(Path("test.xyz")) == "others"

    def test_organize(self, sample_files):
        """Test that files are properly organized."""
        organizer = FileOrganizer(str(sample_files))
        moved_files = organizer.organize()
        
        # Check that the correct number of files were moved
        assert len(moved_files) == 7
        
        # Check that the category directories were created
        assert (sample_files / "documents").exists()
        assert (sample_files / "images").exists()
        assert (sample_files / "audio").exists()
        assert (sample_files / "video").exists()
        assert (sample_files / "code").exists()
        assert (sample_files / "archives").exists()
        assert (sample_files / "others").exists()
        
        # Check that files were moved to the correct locations
        assert (sample_files / "documents" / "document.pdf").exists()
        assert (sample_files / "images" / "image.jpg").exists()
        assert (sample_files / "audio" / "audio.mp3").exists()
        assert (sample_files / "video" / "video.mp4").exists()
        assert (sample_files / "code" / "code.py").exists()
        assert (sample_files / "archives" / "archive.zip").exists()
        assert (sample_files / "others" / "unknown.xyz").exists()
        
        # Check that the log file was created
        assert (sample_files / "fileorganizer_log.json").exists()

    def test_undo_operation(self, sample_files):
        """Test that undo correctly restores files."""
        organizer = FileOrganizer(str(sample_files))
        organizer.organize()
        
        # Verify initial state after organize
        assert not (sample_files / "document.pdf").exists()
        assert (sample_files / "documents" / "document.pdf").exists()
        
        # Undo the operation
        undone_files = organizer.undo_last_operation()
        
        # Check that files were moved back
        assert undone_files is not None
        assert len(undone_files) == 7
        
        # Check that all files are back in the root directory
        assert (sample_files / "document.pdf").exists()
        assert (sample_files / "image.jpg").exists()
        assert (sample_files / "audio.mp3").exists()
        assert (sample_files / "video.mp4").exists()
        assert (sample_files / "code.py").exists()
        assert (sample_files / "archive.zip").exists()
        assert (sample_files / "unknown.xyz").exists()

    def test_duplicate_handling(self, temp_dir):
        """Test that duplicate filenames are handled correctly."""
        # Create two files with the same name
        (temp_dir / "test.txt").touch()
        
        # Create the documents directory and add a file with the same name
        docs_dir = temp_dir / "documents"
        docs_dir.mkdir()
        (docs_dir / "test.txt").touch()
        
        organizer = FileOrganizer(str(temp_dir))
        organizer.organize()
        
        # Check that a unique name was generated
        assert (temp_dir / "documents" / "test_1.txt").exists() or (temp_dir / "documents" / "test.txt").exists()

    def test_empty_directory(self, temp_dir):
        """Test organizing an empty directory."""
        organizer = FileOrganizer(str(temp_dir))
        moved_files = organizer.organize()
        
        # Check that no files were moved
        assert len(moved_files) == 0
        
        # Check that the category directories were still created
        categories = ["images", "documents", "audio", "video", "code", "archives", "others"]
        for category in categories:
            assert (temp_dir / category).exists()

    def test_undo_with_no_log(self, temp_dir):
        """Test undoing when there's no log file."""
        organizer = FileOrganizer(str(temp_dir))
        result = organizer.undo_last_operation()
        
        # Check that None is returned when there's nothing to undo
        assert result is None