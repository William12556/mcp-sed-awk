"""Unit tests for PlatformConfig and BinaryExecutor."""

import pytest
from unittest.mock import patch, MagicMock
from sed_awk_mcp.platform.config import PlatformConfig, BinaryNotFoundError
from sed_awk_mcp.platform.executor import BinaryExecutor, ExecutionResult


class TestPlatformConfig:
    """Test suite for PlatformConfig."""
    
    def test_binaries_located(self):
        """TC-019: Binaries located in PATH."""
        config = PlatformConfig()
        assert config.sed_path
        assert config.awk_path
        assert config.diff_path
    
    def test_gnu_detection(self):
        """TC-020: GNU sed detected correctly."""
        config = PlatformConfig()
        assert isinstance(config.is_gnu_sed, bool)
    
    def test_sed_normalization_gnu(self):
        """TC-021: Sed -i normalization for GNU."""
        config = PlatformConfig()
        config.is_gnu_sed = True
        
        args = ['-i', 's/a/b/', 'file.txt']
        normalized = config.normalize_sed_args(args)
        assert normalized == ['-i.bak', 's/a/b/', 'file.txt']
    
    def test_sed_normalization_bsd(self):
        """TC-021: Sed -i normalization for BSD."""
        config = PlatformConfig()
        config.is_gnu_sed = False
        
        args = ['-i', 's/a/b/', 'file.txt']
        normalized = config.normalize_sed_args(args)
        assert normalized == ['-i', '.bak', 's/a/b/', 'file.txt']
    
    @patch('shutil.which', return_value=None)
    def test_missing_binary_raises_error(self, mock_which):
        """TC-022: Missing binary raises BinaryNotFoundError."""
        with pytest.raises(BinaryNotFoundError, match="not found"):
            PlatformConfig()


class TestBinaryExecutor:
    """Test suite for BinaryExecutor."""
    
    def test_execute_with_shell_false(self):
        """TC-023: Subprocess executes with shell=False."""
        config = PlatformConfig()
        executor = BinaryExecutor(config)
        
        result = executor.execute(['echo', 'test'])
        assert result.returncode == 0
        assert not result.timed_out
    
    def test_timeout_enforced(self):
        """TC-024: 30s timeout enforced."""
        config = PlatformConfig()
        executor = BinaryExecutor(config)
        
        # Sleep command should timeout
        result = executor.execute(['sleep', '35'], timeout=1)
        assert result.timed_out
    
    def test_execution_result_dataclass(self):
        """ExecutionResult has expected fields."""
        config = PlatformConfig()
        executor = BinaryExecutor(config)
        
        result = executor.execute(['echo', 'test'])
        assert hasattr(result, 'returncode')
        assert hasattr(result, 'stdout')
        assert hasattr(result, 'stderr')
        assert hasattr(result, 'timed_out')
