#!/usr/bin/env python3
"""sed-awk-diff MCP Server entry point.

This module provides the main FastMCP server implementation with component
initialization, configuration parsing, and tool registration.
"""

import logging
import os
import sys
from typing import List, Optional

from .mcp_instance import mcp
from .security.validator import SecurityValidator
from .security.path_validator import PathValidator, SecurityError
from .security.audit import AuditLogger
from .platform.config import PlatformConfig, BinaryNotFoundError
from .platform.executor import BinaryExecutor

# Import all tool modules to register their @mcp.tool decorators
from .tools import sed_tool, awk_tool, diff_tool, list_tool

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global component instances
platform_config: Optional[PlatformConfig] = None
path_validator: Optional[PathValidator] = None
security_validator: Optional[SecurityValidator] = None
audit_logger: Optional[AuditLogger] = None
binary_executor: Optional[BinaryExecutor] = None


def parse_allowed_directories(args: List[str]) -> List[str]:
    """Parse allowed directories from command line arguments or environment.
    
    Args:
        args: Command line arguments (sys.argv[1:])
        
    Returns:
        List of allowed directory paths
        
    Raises:
        ValueError: If no directories are specified or paths are invalid
    """
    allowed_dirs = []
    
    # First try command line arguments
    if args:
        allowed_dirs = args
        logger.info("Using allowed directories from command line: %s", allowed_dirs)
    
    # Fall back to environment variable
    elif 'ALLOWED_DIRECTORIES' in os.environ:
        env_dirs = os.environ['ALLOWED_DIRECTORIES']
        allowed_dirs = [d.strip() for d in env_dirs.split(',') if d.strip()]
        logger.info("Using allowed directories from environment: %s", allowed_dirs)
    
    # Default fallback (current working directory)
    else:
        allowed_dirs = [os.getcwd()]
        logger.warning(
            "No directories specified, using current directory: %s", 
            allowed_dirs
        )
    
    if not allowed_dirs:
        raise ValueError("No allowed directories specified")
    
    # Validate directories exist
    for directory in allowed_dirs:
        if not os.path.exists(directory):
            raise ValueError(f"Directory does not exist: {directory}")
        if not os.path.isdir(directory):
            raise ValueError(f"Path is not a directory: {directory}")
    
    return allowed_dirs


def initialize_components(allowed_dirs: List[str]) -> None:
    """Initialize all domain components and inject into tool modules.
    
    Args:
        allowed_dirs: List of allowed directory paths
        
    Raises:
        BinaryNotFoundError: If required binaries are not found
        ValueError: If component initialization fails
    """
    global platform_config, path_validator, security_validator
    global audit_logger, binary_executor
    
    logger.info("Initializing components...")
    
    try:
        # Initialize platform components
        logger.debug("Initializing platform configuration...")
        platform_config = PlatformConfig()
        
        # Initialize security components
        logger.debug("Initializing security components...")
        path_validator = PathValidator(allowed_dirs)
        security_validator = SecurityValidator()
        audit_logger = AuditLogger()
        
        # Initialize execution component
        logger.debug("Initializing binary executor...")
        binary_executor = BinaryExecutor(platform_config)
        
        # Inject components into tool modules
        logger.debug("Injecting components into tool modules...")
        
        sed_tool.initialize_components(
            allowed_dirs,
            security_validator,
            audit_logger,
            platform_config,
            binary_executor
        )
        
        awk_tool.initialize_components(
            allowed_dirs,
            security_validator,
            audit_logger,
            platform_config,
            binary_executor
        )
        
        diff_tool.initialize_components(
            allowed_dirs,
            audit_logger,
            platform_config,
            binary_executor
        )
        
        list_tool.initialize_components(
            allowed_dirs,
            audit_logger
        )
        
        logger.info("Component initialization completed successfully")
        
    except BinaryNotFoundError as e:
        logger.error("Required binary not found: %s", e)
        raise
    except Exception as e:
        logger.error("Component initialization failed: %s", e)
        raise


def create_server(allowed_dirs: List[str]):
    """Create and configure the FastMCP server instance.

    Args:
        allowed_dirs: List of allowed directory paths

    Returns:
        Configured FastMCP server instance
    """
    # Initialize all components
    initialize_components(allowed_dirs)

    # Tools are automatically registered via @mcp.tool() decorators
    # when the tool modules are imported. The shared mcp instance
    # is imported from mcp_instance module.

    logger.info("FastMCP server created successfully")
    return mcp


def main() -> None:
    """Main entry point for the sed-awk-diff MCP server.
    
    Parses configuration, initializes components, creates the server,
    and starts the FastMCP server.
    """
    try:
        # Parse allowed directories from command line or environment
        allowed_dirs = parse_allowed_directories(sys.argv[1:])
        
        # Create and configure server
        mcp = create_server(allowed_dirs)
        
        # Log startup information
        logger.info("=" * 60)
        logger.info("Starting sed-awk-diff MCP Server")
        logger.info("=" * 60)
        logger.info("Allowed directories: %s", allowed_dirs)
        logger.info(
            "Platform: %s sed detected", 
            'GNU' if platform_config.is_gnu_sed else 'BSD'
        )
        logger.info("Binary paths: %s", platform_config.binaries)
        logger.info("Server ready - waiting for MCP client connections...")
        
        # Log to audit system
        audit_logger.log_execution(
            tool="server",
            operation="startup",
            success=True,
            details={
                "allowed_directories": allowed_dirs,
                "platform": "GNU" if platform_config.is_gnu_sed else "BSD",
                "binaries": platform_config.binaries
            }
        )
        
        # Start the FastMCP server (blocks until shutdown)
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping server...")
        if audit_logger:
            audit_logger.log_execution(
                tool="server",
                operation="shutdown",
                success=True,
                details={"reason": "keyboard_interrupt"}
            )
        
    except BinaryNotFoundError as e:
        error_msg = f"Required binary not found: {e}"
        logger.error(error_msg)
        if audit_logger:
            audit_logger.log_execution(
                tool="server",
                operation="startup",
                success=False,
                details={"error": str(e)}
            )
        print(f"Error: {error_msg}", file=sys.stderr)
        sys.exit(1)
        
    except ValueError as e:
        error_msg = f"Configuration error: {e}"
        logger.error(error_msg)
        print(f"Error: {error_msg}", file=sys.stderr)
        print("\nUsage: python -m sed_awk_mcp.server <directory1> [directory2] ...", file=sys.stderr)
        print("   OR: ALLOWED_DIRECTORIES=dir1,dir2 python -m sed_awk_mcp.server", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg, exc_info=True)
        if audit_logger:
            audit_logger.log_execution(
                tool="server",
                operation="startup", 
                success=False,
                details={"error": str(e)}
            )
        print(f"Error: {error_msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()