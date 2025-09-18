"""
Unit tests for the CLI functionality of FileOrganizer.
"""

import shutil
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch

from fileorganizer.cli import main


class TestFileOrganizerCLI:
    """Test suite for FileOrganizer CLI."""

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
        return temp_dir

    def test_organize_command(self, sample_files):
        """Test the organize command."""
        with patch('sys.argv', ['fileorganizer', 'organize', str(sample_files)]):
            result = main()
            assert result == 0

            # Check that the directory structure was created
            assert (sample_files / "documents").exists()
            assert (sample_files / "images").exists()

            # Check that files were moved
            assert (sample_files / "documents" / "document.pdf").exists()
            assert (sample_files / "images" / "image.jpg").exists()

    def test_undo_command(self, sample_files):
        """Test the undo command."""
        # First organize
        with patch('sys.argv', ['fileorganizer', 'organize', str(sample_files)]):
            main()

        # Then undo
        with patch('sys.argv', ['fileorganizer', 'undo', str(sample_files)]):
            result = main()
            assert result == 0

            # Check that files are back in the root directory
            assert (sample_files / "document.pdf").exists()
            assert (sample_files / "image.jpg").exists()

    def test_nonexistent_directory(self):
        """Test handling of nonexistent directories."""
        with patch('sys.argv', ['fileorganizer', 'organize', '/nonexistent/directory']):
            result = main()
            assert result != 0  # Should return error code

    def test_help_command(self):
        """Test the help output."""
        with patch('sys.argv', ['fileorganizer', '--help']), \
             patch('sys.stdout'):  # Capture stdout to prevent printing in tests
            try:
                main()
            except SystemExit as e:
                # argparse's help command usually exits
                assert e.code == 0

    def test_no_command(self):
        """Test when no command is provided."""
        with patch('sys.argv', ['fileorganizer']):
            result = main()
            assert result == 0  # Should show help and exit