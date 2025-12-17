"""AWK tool for MCP server - text transformation and field extraction.

This module implements the awk_transform tool with comprehensive security
validation, field separator support, and optional output file handling.
"""

import logging
from pathlib import Path
from typing import Optional

from ..mcp_instance import mcp
from ..security.validator import SecurityValidator, ValidationError
from ..security.path_validator import PathValidator, SecurityError
from ..security.audit import AuditLogger
from ..platform.config import PlatformConfig, BinaryNotFoundError
from ..platform.executor import BinaryExecutor, TimeoutError, ExecutionError

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

logger = logging.getLogger(__name__)

# Resource limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class ResourceError(Exception):
    """Raised when resource limits are exceeded."""
    pass


# Component references (will be initialized by main server)
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
        "AwkTool initialized with %d allowed directories",
        len(allowed_directories)
    )


@mcp.tool()
async def awk_transform(
    file_path: str,
    program: str,
    field_separator: Optional[str] = None,
    output_file: Optional[str] = None
) -> str:
    """Apply AWK transformation to a file for field extraction and text processing.
    
    Executes an AWK program on the specified file with comprehensive security
    validation and optional output to a file. Supports custom field separators
    and returns either the transformed text or a confirmation message.
    
    Args:
        file_path: Path to the input file
        program: AWK program to execute (e.g., '{print $1}', '{sum += $1} END {print sum}')
        field_separator: Optional field separator character/string (default: whitespace)
        output_file: Optional path to write output (if not specified, returns output)
        
    Returns:
        If output_file specified: confirmation message with file path
        If no output_file: transformed text output from AWK program
        
    Raises:
        ValidationError: If AWK program contains forbidden functions
        SecurityError: If file paths are outside allowed directories
        ResourceError: If input file exceeds size limits
        ExecutionError: If AWK execution fails
    """
    if not all([security_validator, path_validator, audit_logger, platform_config, binary_executor]):
        raise RuntimeError("Tools not initialized - call initialize_components() first")
    
    try:
        # Step 1: Validate AWK program for security
        security_validator.validate_awk_program(program)
        logger.debug("awk_transform: program validation passed")
        
        # Step 2: Validate and resolve input file path
        validated_input = path_validator.validate_path(file_path)
        logger.debug("awk_transform: input path validation passed: %s", validated_input)
        
        # Step 3: Check input file exists and size limits
        if not validated_input.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not validated_input.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        file_size = validated_input.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ResourceError(
                f"File size {file_size} bytes exceeds limit of {MAX_FILE_SIZE} bytes"
            )
        
        logger.debug("awk_transform: file checks passed, size=%d bytes", file_size)
        
        # Step 4: Validate output file path if provided
        validated_output = None
        if output_file:
            validated_output = path_validator.validate_path(output_file)
            logger.debug("awk_transform: output path validation passed: %s", validated_output)
            
            # Ensure output directory exists
            validated_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Step 5: Build AWK command arguments
        args = []
        
        # Add field separator if specified
        if field_separator:
            args.extend(['-F', field_separator])
            logger.debug("awk_transform: using field separator: %s", field_separator)
        
        # Add the AWK program
        args.append(program)
        
        # Add input file
        args.append(str(validated_input))
        
        logger.debug("awk_transform: built args: %s", args)
        
        # Step 6: Normalize arguments for platform
        normalized_args = platform_config.normalize_awk_args(args)
        logger.debug("awk_transform: normalized args: %s", normalized_args)
        
        # Step 7: Execute AWK command
        result = binary_executor.execute(
            ['awk'] + normalized_args,
            timeout=60  # AWK might take longer for complex processing
        )
        
        # Step 8: Check execution result
        if not result.success:
            error_msg = f"AWK execution failed (exit code {result.returncode}): {result.stderr}"
            logger.error("awk_transform: %s", error_msg)
            
            # Log the failure
            audit_logger.log_execution(
                tool="awk_transform",
                operation="transform",
                path=str(validated_input),
                success=False,
                details={
                    "error": result.stderr,
                    "program": program[:100],
                    "field_separator": field_separator,
                    "output_file": output_file
                }
            )
            
            raise ExecutionError(error_msg)
        
        # Step 9: Handle output
        if validated_output:
            # Write output to specified file
            try:
                validated_output.write_text(result.stdout, encoding='utf-8')
                logger.info("awk_transform: output written to %s", validated_output)
                
                # Log successful file output operation
                audit_logger.log_execution(
                    tool="awk_transform",
                    operation=f"transform to file",
                    path=str(validated_input),
                    success=True,
                    details={
                        "program": program[:100],
                        "field_separator": field_separator,
                        "output_file": str(validated_output),
                        "output_size": len(result.stdout),
                        "file_size": file_size
                    }
                )
                
                return f"AWK transformation completed. Output written to {output_file}"
                
            except Exception as write_error:
                logger.error("awk_transform: failed to write output file: %s", write_error)
                raise ExecutionError(f"Failed to write output file: {write_error}")
        
        else:
            # Return stdout directly
            logger.info("awk_transform: returning stdout output (%d chars)", len(result.stdout))
            
            # Log successful stdout operation
            audit_logger.log_execution(
                tool="awk_transform",
                operation="transform",
                path=str(validated_input),
                success=True,
                details={
                    "program": program[:100],
                    "field_separator": field_separator,
                    "output_size": len(result.stdout),
                    "file_size": file_size
                }
            )
            
            return result.stdout
            
    except (ValidationError, SecurityError) as e:
        # Log security/validation failures
        audit_logger.log_validation_failure(
            tool="awk_transform",
            reason=str(e),
            details={
                "file_path": file_path,
                "program": program[:100],
                "field_separator": field_separator,
                "output_file": output_file
            }
        )
        raise
    
    except Exception as e:
        logger.error("awk_transform: unexpected error: %s", e)
        
        # Log execution failure
        audit_logger.log_execution(
            tool="awk_transform",
            operation="transform",
            path=file_path,
            success=False,
            details={
                "error": str(e),
                "program": program[:100],
                "field_separator": field_separator,
                "output_file": output_file
            }
        )
        raise