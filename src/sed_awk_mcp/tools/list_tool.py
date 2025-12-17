"""List tool for MCP server - display allowed directories.

This module implements the list_allowed_directories tool to show the
configured directory whitelist to MCP clients for transparency.
"""

import logging
from typing import Optional

from ..mcp_instance import mcp
from ..security.path_validator import PathValidator
from ..security.audit import AuditLogger

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

logger = logging.getLogger(__name__)

# Component references (will be initialized by main server)
path_validator: Optional[PathValidator] = None
audit_logger: Optional[AuditLogger] = None


def initialize_components(
    allowed_directories: list[str],
    audit_log: Optional[AuditLogger] = None
) -> None:
    """Initialize tool components.
    
    Args:
        allowed_directories: List of allowed directory paths
        audit_log: AuditLogger instance (optional)
    """
    global path_validator, audit_logger
    
    # Initialize with provided instances or create new ones
    path_validator = PathValidator(allowed_directories)
    audit_logger = audit_log or AuditLogger()
    
    logger.info(
        "ListTool initialized with %d allowed directories",
        len(allowed_directories)
    )


@mcp.tool()
async def list_allowed_directories() -> str:
    """List all directories that are accessible to the MCP tools.
    
    Returns a formatted list of all directories that have been configured
    as allowed for file operations. This helps users understand what
    paths they can access through the sed, awk, and diff tools.
    
    Returns:
        Formatted bulleted list of allowed directory paths, or a message
        if no directories are configured
    """
    if not path_validator:
        raise RuntimeError("Tool not initialized - call initialize_components() first")
    
    try:
        # Get the list of allowed directories from PathValidator
        allowed_dirs = path_validator.list_allowed()
        
        logger.debug(
            "list_allowed_directories: retrieved %d allowed directories",
            len(allowed_dirs)
        )
        
        # Handle empty list case
        if not allowed_dirs:
            logger.warning("list_allowed_directories: no allowed directories configured")
            
            # Log the query for audit purposes
            audit_logger.log_execution(
                tool="list_allowed_directories",
                operation="list (empty)",
                success=True,
                details={"count": 0}
            )
            
            return "No allowed directories configured"
        
        # Format as bulleted list
        lines = ["Allowed directories:"]
        
        # Sort directories for consistent output
        for dir_path in sorted(allowed_dirs):
            lines.append(f"- {dir_path}")
        
        result = "\n".join(lines)
        
        logger.info(
            "list_allowed_directories: returning %d directories",
            len(allowed_dirs)
        )
        
        # Log successful query
        audit_logger.log_execution(
            tool="list_allowed_directories",
            operation="list",
            success=True,
            details={
                "count": len(allowed_dirs),
                "directories": allowed_dirs[:10]  # Log first 10 for audit
            }
        )
        
        return result
        
    except Exception as e:
        logger.error("list_allowed_directories: unexpected error: %s", e)
        
        # Log the failure
        audit_logger.log_execution(
            tool="list_allowed_directories",
            operation="list",
            success=False,
            details={"error": str(e)}
        )
        
        raise RuntimeError(f"Failed to list allowed directories: {e}") from e