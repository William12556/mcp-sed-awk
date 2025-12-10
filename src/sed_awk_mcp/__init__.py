"""sed-awk-diff MCP Server package.

A secure MCP (Model Context Protocol) server that provides sed, awk, and diff
tools with comprehensive security validation, path restrictions, and audit logging.

Main modules:
- server: Main FastMCP server entry point
- security: Security validation and audit logging components  
- platform: Platform detection and binary execution components
- tools: MCP tool implementations (sed, awk, diff, list)
"""

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

__version__ = "1.0.0"
__author__ = "William Watson"
__license__ = "MIT"

# Import main server function for easy access
from .server import main, create_server

__all__ = ["main", "create_server", "__version__"]