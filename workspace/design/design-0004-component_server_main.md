Created: 2025 December 10

# Component Design: Server Main

## Document Information

**Document ID:** design-0004-component_server_main
**Document Type:** Component Design (Tier 3)
**Parent Domain:** [design-0004-domain_server](<design-0004-domain_server.md>)
**Status:** Draft
**Version:** 1.0
**Author:** William Watson
**Date:** 2025-12-10

## Table of Contents

1. [Component Information](<#1.0 component information>)
2. [Implementation](<#2.0 implementation>)
3. [Testing](<#3.0 testing>)

---

## 1.0 Component Information

**Component Name:** Server Main

**Purpose:** Application entry point with component initialization and FastMCP server creation.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation

```python
#!/usr/bin/env python3
"""sed-awk-diff MCP Server entry point."""

import sys
import logging
from fastmcp import FastMCP

from sed_awk_mcp.security import SecurityValidator, PathValidator, AuditLogger
from sed_awk_mcp.platform import PlatformConfig, BinaryExecutor
from sed_awk_mcp.config import parse_arguments
from sed_awk_mcp import tools

# Global instances (injected into tool modules)
platform_config: PlatformConfig
path_validator: PathValidator
security_validator: SecurityValidator
audit_logger: AuditLogger
binary_executor: BinaryExecutor

def initialize_components(allowed_dirs: list[str]) -> None:
    """Initialize all domain components."""
    global platform_config, path_validator, security_validator
    global audit_logger, binary_executor
    
    # Platform
    platform_config = PlatformConfig()
    
    # Security
    path_validator = PathValidator(allowed_dirs)
    security_validator = SecurityValidator()
    audit_logger = AuditLogger()
    
    # Execution
    binary_executor = BinaryExecutor()
    
    # Inject into tool modules
    tools.sed.initialize(
        platform_config,
        path_validator,
        security_validator,
        audit_logger,
        binary_executor
    )
    tools.awk.initialize(
        platform_config,
        path_validator,
        security_validator,
        audit_logger,
        binary_executor
    )
    tools.diff.initialize(
        platform_config,
        path_validator,
        audit_logger,
        binary_executor
    )
    tools.list.initialize(path_validator)

def main() -> None:
    """Entry point."""
    # Parse configuration
    allowed_dirs = parse_arguments(sys.argv[1:])
    
    # Initialize components
    initialize_components(allowed_dirs)
    
    # Log startup
    audit_logger._logger.info(f"Starting sed-awk-diff MCP server")
    audit_logger._logger.info(f"Allowed directories: {allowed_dirs}")
    audit_logger._logger.info(
        f"Platform: {'GNU sed' if platform_config.is_gnu_sed else 'BSD sed'}"
    )
    
    # Create and run FastMCP server
    mcp = FastMCP("sed-awk-diff")
    
    # Tools auto-discovered via @mcp.tool() decorators
    
    audit_logger._logger.info("Server ready")
    mcp.run()

if __name__ == "__main__":
    main()
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Testing

```python
def test_initialization():
    """Components initialize correctly."""
    allowed_dirs = ['/tmp/test']
    
    initialize_components(allowed_dirs)
    
    assert platform_config is not None
    assert path_validator is not None
    assert security_validator is not None

def test_main_entry_point(monkeypatch):
    """Main function executes without errors."""
    # Mock FastMCP.run() to prevent blocking
    mock_run_called = False
    def mock_run(self):
        nonlocal mock_run_called
        mock_run_called = True
    
    monkeypatch.setattr(FastMCP, 'run', mock_run)
    monkeypatch.setattr(sys, 'argv', ['server.py', '/tmp/test'])
    
    main()
    
    assert mock_run_called
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
