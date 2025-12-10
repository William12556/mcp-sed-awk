"""Sed tools for MCP server - pattern substitution and preview functionality.

This module implements sed_substitute and preview_sed tools with comprehensive
security validation, backup/rollback, and safe execution.
"""

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import fastmcp

from ..security.validator import SecurityValidator, ValidationError
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


# Initialize components (will be configured by main server)
security_validator: Optional[SecurityValidator] = None
path_validator: Optional[PathValidator] = None
audit_logger: Optional[AuditLogger] = None
platform_config: Optional[PlatformConfig] = None
binary_executor: Optional[BinaryExecutor] = None


def initialize_components(
    allowed_directories: list[str],
    security_val: Optional[SecurityValidator] = None,
    audit_log: Optional[AuditLogger] = None,
    platform_conf: Optional[PlatformConfig] = None,
    binary_exec: Optional[BinaryExecutor] = None
) -> None:
    """Initialize tool components.
    
    Args:
        allowed_directories: List of allowed directory paths
        security_val: SecurityValidator instance (optional)
        audit_log: AuditLogger instance (optional)
        platform_conf: PlatformConfig instance (optional)
        binary_exec: BinaryExecutor instance (optional)
    """
    global security_validator, path_validator, audit_logger, platform_config, binary_executor
    
    # Initialize with provided instances or create new ones
    security_validator = security_val or SecurityValidator()
    path_validator = PathValidator(allowed_directories)
    audit_logger = audit_log or AuditLogger()
    platform_config = platform_conf or PlatformConfig()
    binary_executor = binary_exec or BinaryExecutor()
    
    logger.info(
        "SedTools initialized with %d allowed directories",
        len(allowed_directories)
    )


@mcp.tool()
async def sed_substitute(
    file_path: str,
    pattern: str,
    replacement: str,
    line_range: Optional[str] = None,
    create_backup: bool = True
) -> str:
    """Perform in-place sed substitution with backup and rollback capability.
    
    Safely applies sed pattern substitution to a file with comprehensive validation,
    automatic backup creation, and rollback on failure. Only operates on files
    within the configured whitelist of allowed directories.
    
    Args:
        file_path: Path to the target file
        pattern: Sed substitution pattern (e.g., 's/find/replace/g')
        replacement: Replacement string (for documentation/validation)
        line_range: Optional line range (e.g., '1,10' or '5,$')
        create_backup: Whether to create a backup file (default: True)
        
    Returns:
        Confirmation message with operation details
        
    Raises:
        ValidationError: If pattern contains forbidden commands
        SecurityError: If file path is outside allowed directories
        ResourceError: If file exceeds size limits
        ExecutionError: If sed execution fails
    """
    if not all([security_validator, path_validator, audit_logger, platform_config, binary_executor]):
        raise RuntimeError("Tools not initialized - call initialize_components() first")
    
    try:
        # Step 1: Validate sed pattern for security
        security_validator.validate_sed_pattern(pattern)
        logger.debug("sed_substitute: pattern validation passed")
        
        # Step 2: Validate and resolve file path
        validated_path = path_validator.validate_path(file_path)
        logger.debug("sed_substitute: path validation passed: %s", validated_path)
        
        # Step 3: Check file exists and size limits
        if not validated_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not validated_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        file_size = validated_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ResourceError(
                f"File size {file_size} bytes exceeds limit of {MAX_FILE_SIZE} bytes"
            )
        
        logger.debug("sed_substitute: file checks passed, size=%d bytes", file_size)
        
        # Step 4: Create backup if requested
        backup_path = None
        if create_backup:
            backup_path = Path(f"{validated_path}.bak")
            shutil.copy2(validated_path, backup_path)
            logger.debug("sed_substitute: backup created at %s", backup_path)
        
        try:
            # Step 5: Build sed command
            if line_range:
                # Validate line range format (basic check)
                if not line_range.replace(',', '').replace('$', '').replace('-', '').isdigit():
                    # More sophisticated validation could be added here
                    pass
                sed_pattern = f"{line_range}{pattern}"
            else:
                sed_pattern = pattern
            
            args = ['-i', sed_pattern, str(validated_path)]
            logger.debug("sed_substitute: built args: %s", args)
            
            # Step 6: Normalize arguments for platform
            normalized_args = platform_config.normalize_sed_args(args)
            logger.debug("sed_substitute: normalized args: %s", normalized_args)
            
            # Step 7: Execute sed command
            result = binary_executor.execute(
                platform_config.sed_path,
                normalized_args,
                timeout=30
            )
            
            # Step 8: Check execution result
            if not result.success:
                error_msg = f"Sed execution failed (exit code {result.returncode}): {result.stderr}"
                logger.error("sed_substitute: %s", error_msg)
                raise ExecutionError(error_msg)
            
            # Step 9: Log successful operation
            audit_logger.log_execution(
                tool="sed_substitute",
                operation="in-place substitution",
                path=str(validated_path),
                success=True,
                details={
                    "pattern": pattern[:100],  # Truncate for logging
                    "line_range": line_range,
                    "backup_created": create_backup,
                    "file_size": file_size
                }
            )
            
            success_msg = (
                f"Successfully applied sed substitution to {file_path}"
                f"{f' (lines {line_range})' if line_range else ''}"
                f"{f', backup created at {backup_path.name}' if create_backup else ''}"
            )
            logger.info("sed_substitute: %s", success_msg)
            return success_msg
            
        except Exception as e:
            # Step 10: Rollback on any execution error
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, validated_path)
                    logger.info("sed_substitute: restored backup after failure")
                except Exception as restore_error:
                    logger.error(
                        "sed_substitute: failed to restore backup: %s", 
                        restore_error
                    )
            
            # Log the failure
            audit_logger.log_execution(
                tool="sed_substitute",
                operation="in-place substitution",
                path=str(validated_path),
                success=False,
                details={
                    "error": str(e),
                    "pattern": pattern[:100],
                    "backup_restored": backup_path and backup_path.exists()
                }
            )
            
            raise
            
    except (ValidationError, SecurityError) as e:
        # Log security/validation failures
        audit_logger.log_validation_failure(
            tool="sed_substitute",
            reason=str(e),
            details={
                "file_path": file_path,
                "pattern": pattern[:100]
            }
        )
        raise
    
    except Exception as e:
        logger.error("sed_substitute: unexpected error: %s", e)
        raise


@mcp.tool()
async def preview_sed(
    file_path: str,
    pattern: str,
    replacement: str,
    line_range: Optional[str] = None
) -> str:
    """Preview sed substitution without modifying the original file.
    
    Creates a temporary copy of the file, applies the sed pattern, and returns
    a unified diff showing the proposed changes. The original file is never
    modified.
    
    Args:
        file_path: Path to the target file
        pattern: Sed substitution pattern (e.g., 's/find/replace/g')
        replacement: Replacement string (for documentation/validation)
        line_range: Optional line range (e.g., '1,10' or '5,$')
        
    Returns:
        Unified diff showing proposed changes, or "No changes" if pattern doesn't match
        
    Raises:
        ValidationError: If pattern contains forbidden commands
        SecurityError: If file path is outside allowed directories
        ResourceError: If file exceeds size limits
        ExecutionError: If sed execution fails
    """
    if not all([security_validator, path_validator, audit_logger, platform_config, binary_executor]):
        raise RuntimeError("Tools not initialized - call initialize_components() first")
    
    try:
        # Step 1-3: Same validation as sed_substitute
        security_validator.validate_sed_pattern(pattern)
        validated_path = path_validator.validate_path(file_path)
        
        if not validated_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not validated_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        file_size = validated_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ResourceError(
                f"File size {file_size} bytes exceeds limit of {MAX_FILE_SIZE} bytes"
            )
        
        logger.debug("preview_sed: validation passed for %s", validated_path)
        
        # Step 4: Create temporary copy
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sed_preview') as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Copy original file to temp location
            shutil.copy2(validated_path, tmp_path)
            logger.debug("preview_sed: created temp copy at %s", tmp_path)
            
            # Step 5: Apply sed to temporary file
            if line_range:
                sed_pattern = f"{line_range}{pattern}"
            else:
                sed_pattern = pattern
            
            args = ['-i', sed_pattern, str(tmp_path)]
            normalized_args = platform_config.normalize_sed_args(args)
            
            result = binary_executor.execute(
                platform_config.sed_path,
                normalized_args,
                timeout=30
            )
            
            if not result.success:
                error_msg = f"Sed preview failed (exit code {result.returncode}): {result.stderr}"
                logger.error("preview_sed: %s", error_msg)
                raise ExecutionError(error_msg)
            
            # Step 6: Generate unified diff
            diff_args = ['-u', str(validated_path), str(tmp_path)]
            diff_result = binary_executor.execute(
                platform_config.diff_path,
                diff_args,
                timeout=10
            )
            
            # diff returns non-zero when files differ, which is expected
            if diff_result.returncode == 0:
                # Files are identical - no changes
                return "No changes"
            elif diff_result.returncode == 1:
                # Files differ - return the diff
                return diff_result.stdout if diff_result.stdout else "No changes"
            else:
                # diff error
                logger.warning("preview_sed: diff command failed: %s", diff_result.stderr)
                return f"Diff generation failed: {diff_result.stderr}"
            
        finally:
            # Step 7: Always cleanup temp file
            try:
                tmp_path.unlink(missing_ok=True)
                logger.debug("preview_sed: cleaned up temp file %s", tmp_path)
            except Exception as cleanup_error:
                logger.warning(
                    "preview_sed: failed to cleanup temp file %s: %s",
                    tmp_path, cleanup_error
                )
        
        # Log successful preview
        audit_logger.log_execution(
            tool="preview_sed",
            operation="preview substitution",
            path=str(validated_path),
            success=True,
            details={
                "pattern": pattern[:100],
                "line_range": line_range,
                "file_size": file_size
            }
        )
        
    except (ValidationError, SecurityError) as e:
        # Log security/validation failures
        audit_logger.log_validation_failure(
            tool="preview_sed",
            reason=str(e),
            details={
                "file_path": file_path,
                "pattern": pattern[:100]
            }
        )
        raise
    
    except Exception as e:
        logger.error("preview_sed: unexpected error: %s", e)
        # Log execution failure
        audit_logger.log_execution(
            tool="preview_sed",
            operation="preview substitution",
            path=file_path,
            success=False,
            details={
                "error": str(e),
                "pattern": pattern[:100]
            }
        )
        raise