"""Unit tests for PathValidator component."""

import pytest
import tempfile
import os
from pathlib import Path
from sed_awk_mcp.security.path_validator import PathValidator, SecurityError


class TestPathValidator:
    """Test suite for PathValidator."""
    
    def test_valid_path_in_allowed_directory(self):
        """TC-011: Valid path in allowed directory passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator([tmpdir])
            test_file = os.path.join(tmpdir, 'file.txt')
            result = validator.validate_path(test_file)
            assert isinstance(result, Path)
    
    def test_path_traversal_blocked(self):
        """TC-012: Path traversal with ../ blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator([tmpdir])
            traversal_path = os.path.join(tmpdir, '..', '..', 'etc', 'passwd')
            with pytest.raises(SecurityError, match="not in allowed directories"):
                validator.validate_path(traversal_path)
    
    def test_symlink_to_forbidden_location(self):
        """TC-013: Symlink to forbidden location blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator([tmpdir])
            link_path = os.path.join(tmpdir, 'link')
            # Create symlink to /etc
            os.symlink('/etc', link_path)
            
            with pytest.raises(SecurityError):
                validator.validate_path(link_path)
    
    def test_empty_whitelist_raises_error(self):
        """TC-014: Empty whitelist raises ValueError at init."""
        with pytest.raises(ValueError, match="cannot be empty"):
            PathValidator([])
    
    def test_invalid_directory_raises_error(self):
        """TC-015: Invalid directory in whitelist raises ValueError."""
        with pytest.raises(ValueError, match="Invalid directory"):
            PathValidator(['/nonexistent_directory_12345'])
    
    def test_file_as_allowed_dir_raises_error(self):
        """File in allowed_dirs should raise ValueError."""
        with tempfile.NamedTemporaryFile() as tmp:
            with pytest.raises(ValueError, match="Not a directory"):
                PathValidator([tmp.name])
    
    def test_relative_path_resolution(self):
        """Relative paths should be resolved to absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator([tmpdir])
            # Change to tmpdir and use relative path
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = validator.validate_path('file.txt')
                assert result.is_absolute()
            finally:
                os.chdir(old_cwd)
    
    def test_list_allowed_returns_sorted(self):
        """list_allowed should return sorted list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir1 = os.path.join(tmpdir, 'b')
            dir2 = os.path.join(tmpdir, 'a')
            dir3 = os.path.join(tmpdir, 'c')
            os.makedirs(dir1)
            os.makedirs(dir2)
            os.makedirs(dir3)
            
            validator = PathValidator([dir1, dir2, dir3])
            allowed = validator.list_allowed()
            
            assert allowed == sorted(allowed)
    
    def test_subdirectory_access_allowed(self):
        """Files in subdirectories should be accessible."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, 'sub', 'deep')
            os.makedirs(subdir)
            
            validator = PathValidator([tmpdir])
            test_file = os.path.join(subdir, 'file.txt')
            result = validator.validate_path(test_file)
            assert isinstance(result, Path)
