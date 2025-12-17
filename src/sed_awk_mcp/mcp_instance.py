"""Singleton FastMCP instance for sed-awk-diff MCP Server.

This module provides a shared FastMCP instance that all tool modules
use to register their decorators. This ensures that tool registrations
are available to the server instance at runtime.
"""

import fastmcp

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

# Create the singleton FastMCP instance
# All tool modules will import and use this same instance
mcp = fastmcp.FastMCP("sed-awk-mcp")
