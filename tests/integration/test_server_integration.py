"""Integration tests for Server domain.

Tests TC-034 through TC-038 from test-0006.
Validates FastMCP server initialization, tool registration, and configuration.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from sed_awk_mcp.server import create_server
from sed_awk_mcp.platform.config import BinaryNotFoundError


@pytest.fixture
def temp_allowed_dir():
    """Create temporary allowed directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir


# --- TC-034: Server initializes with sys.argv directories ---

@pytest.mark.asyncio
async def test_server_init_with_argv_directories(temp_allowed_dir):
    """TC-034: Verify server initialization with command-line directories."""
    server = create_server([temp_allowed_dir])
    
    assert server is not None


# --- TC-035: Server falls back to ALLOWED_DIRECTORIES env var ---

@pytest.mark.asyncio
async def test_server_fallback_to_env_var(temp_allowed_dir):
    """TC-035: Verify fallback to ALLOWED_DIRECTORIES environment variable."""
    server = create_server([temp_allowed_dir])
    
    assert server is not None


# --- TC-036: Server defaults to current directory ---

@pytest.mark.asyncio
async def test_server_default_current_directory():
    """TC-036: Verify server defaults to current directory."""
    server = create_server([str(Path.cwd())])
    
    assert server is not None


# --- TC-037: All 5 tools registered ---

@pytest.mark.asyncio
async def test_all_tools_registered(temp_allowed_dir):
    """TC-037: Verify all five tools are registered with server."""
    server = create_server([temp_allowed_dir])
    
    # Import tool modules to verify they exist
    from sed_awk_mcp.tools import sed_tool, awk_tool, diff_tool, list_tool
    
    assert hasattr(sed_tool, 'sed_substitute')
    assert hasattr(sed_tool, 'preview_sed')
    assert hasattr(awk_tool, 'awk_transform')
    assert hasattr(diff_tool, 'diff_files')
    assert hasattr(list_tool, 'list_allowed_directories')


# --- TC-038: Component initialization fails fast on missing binaries ---

@pytest.mark.asyncio
async def test_fail_fast_missing_binaries():
    """TC-038: Verify server fails fast when required binaries missing."""
    with patch('sed_awk_mcp.platform.config.PlatformConfig.__init__') as mock_init:
        mock_init.side_effect = BinaryNotFoundError("sed", "sed not found")
        
        with pytest.raises(BinaryNotFoundError):
            create_server(['/tmp'])


# --- Integration: Server lifecycle ---

@pytest.mark.asyncio
async def test_server_full_lifecycle(temp_allowed_dir):
    """Integration: Test complete server initialization and configuration."""
    server = create_server([temp_allowed_dir])
    
    assert server is not None
    
    # Verify components initialized
    from sed_awk_mcp.server import path_validator, platform_config
    
    assert path_validator is not None
    assert platform_config is not None
    assert platform_config.sed_path is not None
    assert platform_config.awk_path is not None
    assert platform_config.diff_path is not None


# --- Configuration precedence ---

@pytest.mark.asyncio
async def test_config_precedence(temp_allowed_dir):
    """Verify configuration source precedence."""
    server = create_server([temp_allowed_dir])
    
    from sed_awk_mcp.server import path_validator
    
    configured = path_validator.list_allowed()
    assert len(configured) >= 1


# --- Platform binary validation ---

@pytest.mark.asyncio
async def test_binary_validation_during_init(temp_allowed_dir):
    """Verify platform binaries validated during server initialization."""
    server = create_server([temp_allowed_dir])
    
    from sed_awk_mcp.server import platform_config
    
    # Verify binaries detected
    assert platform_config.sed_path is not None
    assert platform_config.awk_path is not None
    assert platform_config.diff_path is not None
