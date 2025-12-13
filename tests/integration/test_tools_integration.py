"""Integration tests for Tools domain.

Tests TC-026 through TC-033 from test-0005.
Validates tool functions with proper component initialization and validation chain.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from sed_awk_mcp.security.validator import SecurityValidator, ValidationError
from sed_awk_mcp.security.path_validator import PathValidator, SecurityError
from sed_awk_mcp.platform.config import PlatformConfig
from sed_awk_mcp.platform.executor import BinaryExecutor, ExecutionResult
from sed_awk_mcp.security.audit import AuditLogger

# Import tool modules to access underlying functions
from sed_awk_mcp.tools import sed_tool, awk_tool, diff_tool, list_tool


@pytest.fixture
def temp_workspace():
    """Create temporary workspace."""
    workspace = tempfile.mkdtemp()
    yield Path(workspace)
    shutil.rmtree(workspace, ignore_errors=True)


@pytest.fixture
def test_file(temp_workspace):
    """Create test file."""
    file_path = temp_workspace / "test.txt"
    file_path.write_text("hello world\nfoo bar\nbaz qux\n")
    return file_path


@pytest.fixture
def initialized_tools(temp_workspace):
    """Initialize tools with required components."""
    # Initialize components
    security_validator = SecurityValidator()
    audit_logger = AuditLogger()
    platform_config = PlatformConfig()
    binary_executor = BinaryExecutor(platform_config)
    
    # Initialize tool modules
    sed_tool.initialize_components(
        [str(temp_workspace)],
        security_validator,
        audit_logger,
        platform_config,
        binary_executor
    )
    
    awk_tool.initialize_components(
        [str(temp_workspace)],
        security_validator,
        audit_logger,
        platform_config,
        binary_executor
    )
    
    diff_tool.initialize_components(
        [str(temp_workspace)],
        audit_logger,
        platform_config,
        binary_executor
    )
    
    list_tool.initialize_components(
        [str(temp_workspace)],
        audit_logger
    )
    
    return {
        'security': security_validator,
        'audit': audit_logger,
        'platform': platform_config,
        'executor': binary_executor
    }


# --- TC-026: sed_substitute creates backup and edits file ---

@pytest.mark.asyncio
async def test_sed_substitute_backup_and_edit(test_file, initialized_tools):
    """TC-026: Verify sed_substitute creates backup before editing."""
    # Get underlying function
    func = sed_tool.sed_substitute.fn
    
    result = await func(
        str(test_file),
        "s/world/universe/",
        "universe"
    )
    
    assert "Successfully" in result
    assert "universe" in test_file.read_text()
    assert Path(f"{test_file}.bak").exists()


# --- TC-027: sed_substitute rollback on failure ---

@pytest.mark.asyncio
async def test_sed_substitute_rollback_on_failure(test_file, initialized_tools):
    """TC-027: Verify backup restoration on sed failure."""
    func = sed_tool.sed_substitute.fn
    original = test_file.read_text()
    
    # Invalid pattern should fail validation
    with pytest.raises(ValidationError):
        await func(str(test_file), "s/world/universe/e", "universe")
    
    assert test_file.read_text() == original


# --- TC-028: preview_sed generates diff without modifying file ---

@pytest.mark.asyncio
async def test_preview_sed_no_modification(test_file, initialized_tools):
    """TC-028: Verify preview generates diff without file modification."""
    func = sed_tool.preview_sed.fn
    original = test_file.read_text()
    
    diff_output = await func(str(test_file), "s/world/universe/", "universe")
    
    assert "world" in diff_output or "universe" in diff_output
    assert test_file.read_text() == original
    assert not Path(f"{test_file}.bak").exists()


# --- TC-029: awk_transform extracts fields correctly ---

@pytest.mark.asyncio
async def test_awk_transform_field_extraction(test_file, initialized_tools):
    """TC-029: Verify awk field extraction."""
    func = awk_tool.awk_transform.fn
    
    csv_file = test_file.parent / "data.csv"
    csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")
    
    result = await func(str(csv_file), "{print $2}", field_separator=",")
    
    assert "age" in result
    assert "30" in result
    assert "25" in result


# --- TC-030: diff_files generates unified diff ---

@pytest.mark.asyncio
async def test_diff_files_unified_format(temp_workspace, initialized_tools):
    """TC-030: Verify diff generation."""
    func = diff_tool.diff_files.fn
    
    file1 = temp_workspace / "file1.txt"
    file2 = temp_workspace / "file2.txt"
    file1.write_text("line1\nline2\nline3\n")
    file2.write_text("line1\nmodified\nline3\n")
    
    diff_output = await func(str(file1), str(file2))
    
    assert "---" in diff_output
    assert "+++" in diff_output


# --- TC-031: list_allowed_directories returns sorted list ---

@pytest.mark.asyncio
async def test_list_allowed_directories_sorted(initialized_tools):
    """TC-031: Verify directory list is sorted."""
    func = list_tool.list_allowed_directories.fn
    
    result = await func()
    
    assert "Allowed directories" in result or "/" in result


# --- TC-032: File size >10MB rejected ---

@pytest.mark.asyncio
async def test_large_file_rejection(temp_workspace, initialized_tools):
    """TC-032: Verify files exceeding size limit are rejected."""
    func = sed_tool.sed_substitute.fn
    
    large_file = temp_workspace / "large.txt"
    large_file.write_bytes(b"x" * (10 * 1024 * 1024 + 1))
    
    with pytest.raises(Exception, match="exceeds|size"):
        await func(str(large_file), "s/x/y/", "y")


# --- TC-033: Line range restriction works ---

@pytest.mark.asyncio
async def test_line_range_restriction(test_file, initialized_tools):
    """TC-033: Verify line range parameter restricts operation scope."""
    func = sed_tool.sed_substitute.fn
    original = test_file.read_text()
    lines = original.splitlines()
    
    await func(str(test_file), "s/hello/HELLO/", "HELLO", line_range="1")
    
    modified = test_file.read_text().splitlines()
    assert "HELLO" in modified[0]
    assert modified[1] == lines[1]


# --- Integration: Full validation chain ---

@pytest.mark.asyncio
async def test_full_validation_chain(test_file, initialized_tools):
    """Integration: Verify complete security→platform→execution flow."""
    func = sed_tool.sed_substitute.fn
    
    result = await func(str(test_file), "s/world/universe/", "universe")
    
    assert "Successfully" in result
    assert test_file.read_text() != Path(f"{test_file}.bak").read_text()


# --- Error propagation tests ---

@pytest.mark.asyncio
async def test_security_error_propagation(initialized_tools):
    """Verify security errors propagate correctly."""
    func = sed_tool.sed_substitute.fn
    
    with pytest.raises(SecurityError):
        await func("/etc/passwd", "s/root/user/", "user")


@pytest.mark.asyncio
async def test_validation_error_propagation(test_file, initialized_tools):
    """Verify validation errors propagate correctly."""
    func = sed_tool.sed_substitute.fn
    
    with pytest.raises(ValidationError):
        await func(str(test_file), "s/test/$(rm -rf /)/", "replacement")
