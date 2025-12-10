"""Diff tool for MCP server - file comparison and difference analysis.

This module implements the diff_files tool for generating unified diffs
between two files with comprehensive path validation and audit logging.
"""

import logging
from typing import Optional

import fastmcp

from ..security.path_validator import PathValidator, SecurityError
from ..security.audit import AuditLogger
from ..platform.config import PlatformConfig, BinaryNotFoundError
from ..platform.executor import BinaryExecutor, TimeoutError, ExecutionError

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = fastmcp.FastMCP("sed-awk-mcp")

# Resource limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class ResourceError(Exception):
    """Raised when resource limits are exceeded."""
    pass


# Component references (will be initialized by main server)
path_validator: Optional[PathValidator] = None
audit_logger: Optional[AuditLogger] = None
platform_config: Optional[PlatformConfig] = None
binary_executor: Optional[BinaryExecutor] = None


def initialize_components(
    allowed_directories: list[str],
    audit_log: Optional[AuditLogger] = None,
    platform_conf: Optional[PlatformConfig] = None,
    binary_exec: Optional[BinaryExecutor] = None
) -> None:
    """Initialize tool components.
    
    Args:
        allowed_directories: List of allowed directory paths
        audit_log: AuditLogger instance (optional)
        platform_conf: PlatformConfig instance (optional)
        binary_exec: BinaryExecutor instance (optional)
    """
    global path_validator, audit_logger, platform_config, binary_executor
    
    # Initialize with provided instances or create new ones
    path_validator = PathValidator(allowed_directories)
    audit_logger = audit_log or AuditLogger()
    platform_config = platform_conf or PlatformConfig()
    binary_executor = binary_exec or BinaryExecutor()
    
    logger.info(
        "DiffTool initialized with %d allowed directories",
        len(allowed_directories)
    )


@mcp.tool()
async def diff_files(
    file1_path: str,
    file2_path: str,
    context_lines: int = 3,
    ignore_whitespace: bool = False
) -> str:
    """Generate unified diff between two files.
    
    Compares two files and returns a unified diff showing their differences.
    Only operates on files within the configured whitelist of allowed directories.
    
    Args:
        file1_path: Path to the first file
        file2_path: Path to the second file
        context_lines: Number of context lines to show around changes (default: 3)
        ignore_whitespace: Whether to ignore whitespace differences (default: False)
        
    Returns:
        Unified diff output showing differences, or empty string if files are identical
        
    Raises:
        SecurityError: If either file path is outside allowed directories
        ResourceError: If either file exceeds size limits
        ExecutionError: If diff command execution fails
        FileNotFoundError: If either file does not exist
    """
    if not all([path_validator, audit_logger, platform_config, binary_executor]):
        raise RuntimeError("Tools not initialized - call initialize_components() first")
    
    try:
        # Step 1: Validate and resolve both file paths
        validated_file1 = path_validator.validate_path(file1_path)
        validated_file2 = path_validator.validate_path(file2_path)
        
        logger.debug(
            "diff_files: path validation passed: %s vs %s",
            validated_file1, validated_file2
        )
        
        # Step 2: Check both files exist and are actually files
        if not validated_file1.exists():
            raise FileNotFoundError(f"First file not found: {file1_path}")
        
        if not validated_file2.exists():
            raise FileNotFoundError(f"Second file not found: {file2_path}")
        
        if not validated_file1.is_file():
            raise ValueError(f"First path is not a file: {file1_path}")
        
        if not validated_file2.is_file():
            raise ValueError(f"Second path is not a file: {file2_path}")
        
        # Step 3: Check file size limits
        file1_size = validated_file1.stat().st_size
        file2_size = validated_file2.stat().st_size
        
        if file1_size > MAX_FILE_SIZE:
            raise ResourceError(
                f"First file size {file1_size} bytes exceeds limit of {MAX_FILE_SIZE} bytes"
            )
        
        if file2_size > MAX_FILE_SIZE:
            raise ResourceError(
                f"Second file size {file2_size} bytes exceeds limit of {MAX_FILE_SIZE} bytes"
            )
        
        logger.debug(
            "diff_files: file checks passed, sizes=%d and %d bytes",
            file1_size, file2_size
        )
        
        # Step 4: Build diff command arguments
        args = []
        
        # Use unified format
        args.append('-u')
        
        # Set context lines (validate it's reasonable)
        if context_lines < 0 or context_lines > 100:
            raise ValueError(f"Invalid context_lines value: {context_lines} (must be 0-100)")
        
        if context_lines != 3:  # 3 is the default, no need to specify
            args.append(f'-U{context_lines}')
        
        # Add whitespace ignoring flag if requested
        if ignore_whitespace:
            args.append('-w')
        
        # Add file paths
        args.append(str(validated_file1))
        args.append(str(validated_file2))
        
        logger.debug("diff_files: built args: %s", args)
        
        # Step 5: Normalize arguments for platform
        normalized_args = platform_config.normalize_diff_args(args)
        logger.debug("diff_files: normalized args: %s", normalized_args)
        
        # Step 6: Execute diff command
        result = binary_executor.execute(
            platform_config.diff_path,
            normalized_args,
            timeout=30
        )
        
        # Step 7: Process diff result based on return code
        # diff returns:
        # 0: files are identical
        # 1: files differ
        # 2+: error occurred
        
        if result.returncode == 0:
            # Files are identical
            logger.info("diff_files: files are identical")
            
            # Log successful comparison
            audit_logger.log_execution(
                tool="diff_files",
                operation="compare (identical)",
                path=f"{file1_path} vs {file2_path}",
                success=True,
                details={
                    "file1_size": file1_size,
                    "file2_size": file2_size,
                    "context_lines": context_lines,
                    "ignore_whitespace": ignore_whitespace,
                    "result": "identical"
                }
            )
            
            return ""  # Empty string indicates identical files
            
        elif result.returncode == 1:
            # Files differ - return the diff output
            logger.info(
                "diff_files: files differ, diff output length=%d chars",
                len(result.stdout)
            )
            
            # Log successful comparison
            audit_logger.log_execution(
                tool="diff_files",
                operation="compare (different)",
                path=f"{file1_path} vs {file2_path}",
                success=True,
                details={
                    "file1_size": file1_size,
                    "file2_size": file2_size,
                    "context_lines": context_lines,
                    "ignore_whitespace": ignore_whitespace,
                    "result": "different",
                    "diff_size": len(result.stdout)
                }
            )
            
            return result.stdout
            
        else:
            # Error occurred during diff execution
            error_msg = f"Diff command failed (exit code {result.returncode}): {result.stderr}"
            logger.error("diff_files: %s", error_msg)
            
            # Log the failure
            audit_logger.log_execution(
                tool="diff_files",
                operation="compare",
                path=f"{file1_path} vs {file2_path}",
                success=False,
                details={
                    "error": result.stderr,
                    "exit_code": result.returncode,
                    "file1_size": file1_size,
                    "file2_size": file2_size
                }
            )
            
            raise ExecutionError(error_msg)
            
    except SecurityError as e:
        # Log security/validation failures
        audit_logger.log_validation_failure(
            tool="diff_files",
            reason=str(e),
            details={
                "file1_path": file1_path,
                "file2_path": file2_path,
                "context_lines": context_lines,
                "ignore_whitespace": ignore_whitespace
            }
        )
        raise
    
    except Exception as e:
        logger.error("diff_files: unexpected error: %s", e)
        
        # Log execution failure
        audit_logger.log_execution(
            tool="diff_files",
            operation="compare",
            path=f"{file1_path} vs {file2_path}",
            success=False,
            details={
                "error": str(e),
                "context_lines": context_lines,
                "ignore_whitespace": ignore_whitespace
            }
        )
        raise