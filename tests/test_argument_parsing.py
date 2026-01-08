#!/usr/bin/env python3
"""Unit tests for argument parsing in server.py."""

import os
import pytest
import tempfile
from pathlib import Path

# Import the function to test
from sed_awk_mcp.server import parse_allowed_directories


class TestArgumentParsing:
    """Test suite for parse_allowed_directories function."""
    
    def setup_method(self):
        """Create temporary directories for testing."""
        self.temp_dir1 = tempfile.mkdtemp()
        self.temp_dir2 = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up temporary directories."""
        import shutil
        shutil.rmtree(self.temp_dir1, ignore_errors=True)
        shutil.rmtree(self.temp_dir2, ignore_errors=True)
    
    def test_single_flag_argument(self):
        """Test parsing single --allowed-directory flag."""
        args = ['--allowed-directory', self.temp_dir1]
        result = parse_allowed_directories(args)
        assert result == [self.temp_dir1]
    
    def test_multiple_flag_arguments(self):
        """Test parsing multiple --allowed-directory flags."""
        args = [
            '--allowed-directory', self.temp_dir1,
            '--allowed-directory', self.temp_dir2
        ]
        result = parse_allowed_directories(args)
        assert result == [self.temp_dir1, self.temp_dir2]
    
    def test_positional_arguments(self):
        """Test parsing positional directory arguments."""
        args = [self.temp_dir1, self.temp_dir2]
        result = parse_allowed_directories(args)
        assert result == [self.temp_dir1, self.temp_dir2]
    
    def test_mixed_arguments(self):
        """Test parsing mixed flag and positional arguments."""
        args = [
            '--allowed-directory', self.temp_dir1,
            self.temp_dir2
        ]
        result = parse_allowed_directories(args)
        assert result == [self.temp_dir1, self.temp_dir2]
    
    def test_environment_variable_fallback(self):
        """Test fallback to environment variable when no CLI args."""
        # Save original env var if it exists
        original = os.environ.get('ALLOWED_DIRECTORIES')
        
        try:
            os.environ['ALLOWED_DIRECTORIES'] = f"{self.temp_dir1},{self.temp_dir2}"
            result = parse_allowed_directories([])
            assert result == [self.temp_dir1, self.temp_dir2]
        finally:
            # Restore original env var
            if original is not None:
                os.environ['ALLOWED_DIRECTORIES'] = original
            else:
                os.environ.pop('ALLOWED_DIRECTORIES', None)
    
    def test_current_directory_default(self):
        """Test default to current directory when no configuration."""
        # Ensure no environment variable
        original = os.environ.pop('ALLOWED_DIRECTORIES', None)
        
        try:
            result = parse_allowed_directories([])
            assert result == [os.getcwd()]
        finally:
            # Restore original env var
            if original is not None:
                os.environ['ALLOWED_DIRECTORIES'] = original
    
    def test_nonexistent_directory_raises_error(self):
        """Test that nonexistent directory path raises ValueError."""
        args = ['--allowed-directory', '/nonexistent/directory/path']
        with pytest.raises(ValueError, match="Directory does not exist"):
            parse_allowed_directories(args)
    
    def test_file_instead_of_directory_raises_error(self):
        """Test that file path instead of directory raises ValueError."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            args = ['--allowed-directory', tmp_path]
            with pytest.raises(ValueError, match="Path is not a directory"):
                parse_allowed_directories(args)
        finally:
            os.unlink(tmp_path)
    
    def test_empty_environment_variable(self):
        """Test handling of empty environment variable."""
        original = os.environ.pop('ALLOWED_DIRECTORIES', None)
        
        try:
            os.environ['ALLOWED_DIRECTORIES'] = ''
            result = parse_allowed_directories([])
            # Should fall back to current directory
            assert result == [os.getcwd()]
        finally:
            if original is not None:
                os.environ['ALLOWED_DIRECTORIES'] = original
            else:
                os.environ.pop('ALLOWED_DIRECTORIES', None)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
