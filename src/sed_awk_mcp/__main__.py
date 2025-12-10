"""Command-line interface for sed-awk-diff MCP Server.

This module enables running the server with: python -m sed_awk_mcp
"""

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

from .server import main

if __name__ == "__main__":
    main()