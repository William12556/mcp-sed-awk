Created: 2025 December 10

# Component Design: Server Error Handler

## Document Information

**Document ID:** design-0004-component_server_error
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

**Component Name:** Server Error Handler

**Purpose:** Translate domain exceptions to MCP error responses.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation

```python
from typing import Dict, Any
from fastmcp import FastMCP

from sed_awk_mcp.security import ValidationError, SecurityError
from sed_awk_mcp.platform import ExecutionError, TimeoutError, ResourceError

def register_error_handlers(mcp: FastMCP, audit_logger) -> None:
    """Register error handlers with FastMCP server."""
    
    @mcp.error_handler
    async def handle_error(error: Exception) -> Dict[str, Any]:
        """Translate domain exceptions to MCP errors."""
        
        if isinstance(error, ValidationError):
            return {
                "error": "validation_error",
                "message": str(error),
                "code": "INVALID_INPUT"
            }
        
        elif isinstance(error, SecurityError):
            return {
                "error": "security_error",
                "message": str(error),
                "code": "ACCESS_DENIED"
            }
        
        elif isinstance(error, ResourceError):
            return {
                "error": "resource_error",
                "message": str(error),
                "code": "RESOURCE_LIMIT_EXCEEDED"
            }
        
        elif isinstance(error, TimeoutError):
            return {
                "error": "timeout_error",
                "message": str(error),
                "code": "OPERATION_TIMEOUT"
            }
        
        elif isinstance(error, ExecutionError):
            return {
                "error": "execution_error",
                "message": str(error),
                "code": "OPERATION_FAILED"
            }
        
        else:
            # Unknown error
            audit_logger.log_error("Unhandled exception", error)
            return {
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Testing

```python
def test_validation_error_translation():
    """ValidationError mapped to INVALID_INPUT."""
    error = ValidationError("Pattern contains forbidden command")
    
    result = await handle_error(error)
    
    assert result["code"] == "INVALID_INPUT"
    assert "forbidden" in result["message"].lower()

def test_security_error_translation():
    """SecurityError mapped to ACCESS_DENIED."""
    error = SecurityError("Path outside whitelist")
    
    result = await handle_error(error)
    
    assert result["code"] == "ACCESS_DENIED"

def test_timeout_error_translation():
    """TimeoutError mapped to OPERATION_TIMEOUT."""
    error = TimeoutError("Execution exceeded 30s")
    
    result = await handle_error(error)
    
    assert result["code"] == "OPERATION_TIMEOUT"

def test_unknown_error_logging():
    """Unknown errors logged and return generic message."""
    error = RuntimeError("Unexpected")
    
    result = await handle_error(error)
    
    assert result["code"] == "INTERNAL_ERROR"
    assert result["message"] == "An unexpected error occurred"
    # Verify audit_logger.log_error was called
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
