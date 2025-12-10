Created: 2025 December 10

# Component Design: AuditLogger

## Document Information

**Document ID:** design-0001-component_security_audit
**Document Type:** Component Design (Tier 3)
**Parent Domain:** [design-0001-domain_security](<design-0001-domain_security.md>)
**Status:** Draft
**Version:** 1.0
**Author:** William Watson
**Date:** 2025-12-10

## Table of Contents

1. [Component Information](<#1.0 component information>)
2. [Implementation Details](<#2.0 implementation details>)
3. [Interfaces](<#3.0 interfaces>)
4. [Processing Logic](<#4.0 processing logic>)
5. [Error Handling](<#5.0 error handling>)
6. [Data Structures](<#6.0 data structures>)
7. [Testing Requirements](<#7.0 testing requirements>)

---

## 1.0 Component Information

**Component Name:** AuditLogger

**Purpose:** Record security-relevant events including validation failures, access violations, and operation executions.

**Responsibilities:**
- Security event logging
- Sensitive data sanitization
- Structured log formatting
- Configurable log levels

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation Details

### 2.1 Class Definition

```python
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class AuditLogger:
    """Logs security-relevant events with sanitization."""
    
    def __init__(self, logger_name: str = "sed_awk_mcp.audit") -> None:
        """Initialize audit logger.
        
        Args:
            logger_name: Logger name for hierarchy
        """
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.INFO)
    
    def log_validation_failure(
        self,
        tool: str,
        reason: str,
        details: Dict[str, Any]
    ) -> None:
        """Log input validation failure."""
    
    def log_access_violation(
        self,
        path: str,
        reason: str
    ) -> None:
        """Log path access violation."""
    
    def log_execution(
        self,
        tool: str,
        operation: str,
        path: str,
        success: bool = True
    ) -> None:
        """Log tool execution."""
    
    def log_error(
        self,
        message: str,
        error: Exception
    ) -> None:
        """Log unexpected errors."""
```

### 2.2 Log Sanitization

```python
def _sanitize(self, data: Any) -> Any:
    """Remove sensitive information from log data.
    
    Sanitizes:
    - File contents
    - Pattern details (keep summary only)
    - User input (truncate if long)
    
    Args:
        data: Data to sanitize
        
    Returns:
        Sanitized data safe for logging
    """
    
    if isinstance(data, str):
        # Truncate long strings
        if len(data) > 200:
            return data[:200] + "...[truncated]"
        return data
    
    if isinstance(data, dict):
        # Recursively sanitize dict values
        return {k: self._sanitize(v) for k, v in data.items()}
    
    if isinstance(data, (list, tuple)):
        # Sanitize sequences
        return [self._sanitize(item) for item in data]
    
    return data
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Interfaces

### 3.1 Public Methods

```python
def log_validation_failure(
    self,
    tool: str,
    reason: str,
    details: Dict[str, Any]
) -> None:
    """Log validation failure.
    
    Args:
        tool: Tool name (e.g., "sed_substitute")
        reason: Validation failure reason
        details: Additional context (sanitized before logging)
        
    Log Level: WARNING
    """

def log_access_violation(
    self,
    path: str,
    reason: str
) -> None:
    """Log access control violation.
    
    Args:
        path: Attempted path (sanitized)
        reason: Denial reason
        
    Log Level: WARNING
    """

def log_execution(
    self,
    tool: str,
    operation: str,
    path: str,
    success: bool = True
) -> None:
    """Log tool execution.
    
    Args:
        tool: Tool name
        operation: Operation performed
        path: Target file path
        success: Operation success status
        
    Log Level: INFO (success) or ERROR (failure)
    """

def log_error(
    self,
    message: str,
    error: Exception
) -> None:
    """Log unexpected error.
    
    Args:
        message: Error context
        error: Exception object
        
    Log Level: ERROR
    """
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Processing Logic

### 4.1 Validation Failure Logging

```python
def log_validation_failure(
    self,
    tool: str,
    reason: str,
    details: Dict[str, Any]
) -> None:
    sanitized_details = self._sanitize(details)
    
    self._logger.warning(
        "Validation failure",
        extra={
            "event": "validation_failure",
            "tool": tool,
            "reason": reason,
            "details": sanitized_details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### 4.2 Access Violation Logging

```python
def log_access_violation(
    self,
    path: str,
    reason: str
) -> None:
    # Sanitize path (may contain sensitive directory names)
    sanitized_path = self._sanitize(path)
    
    self._logger.warning(
        "Access violation",
        extra={
            "event": "access_violation",
            "path": sanitized_path,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### 4.3 Execution Logging

```python
def log_execution(
    self,
    tool: str,
    operation: str,
    path: str,
    success: bool = True
) -> None:
    level = logging.INFO if success else logging.ERROR
    message = "Tool execution" if success else "Tool execution failed"
    
    self._logger.log(
        level,
        message,
        extra={
            "event": "execution",
            "tool": tool,
            "operation": operation,
            "path": self._sanitize(path),
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Error Handling

### 5.1 Logging Failures

**Strategy:** Never raise exceptions from logging methods.

```python
def log_validation_failure(self, tool: str, reason: str, details: Dict) -> None:
    try:
        # Logging logic
        ...
    except Exception as e:
        # Fallback to stderr if logging fails
        print(f"Audit logging failed: {e}", file=sys.stderr)
```

### 5.2 Sanitization Errors

```python
def _sanitize(self, data: Any) -> Any:
    try:
        # Sanitization logic
        ...
    except Exception:
        # Return safe placeholder on sanitization failure
        return "[sanitization error]"
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Data Structures

### 6.1 Log Event Structure

```python
{
    "event": str,           # Event type: validation_failure, access_violation, execution
    "timestamp": str,       # ISO 8601 UTC timestamp
    "tool": str,           # Tool name (optional)
    "reason": str,         # Event reason (optional)
    "path": str,           # File path (optional, sanitized)
    "details": Dict,       # Additional context (sanitized)
    "success": bool        # Operation success (execution events only)
}
```

### 6.2 Example Logs

**Validation failure:**
```python
{
    "event": "validation_failure",
    "timestamp": "2025-12-10T10:30:45.123Z",
    "tool": "sed_substitute",
    "reason": "Forbidden sed command detected: 'e'",
    "details": {
        "pattern": "s/old/new/e",
        "file": "/tmp/test.txt"
    }
}
```

**Access violation:**
```python
{
    "event": "access_violation",
    "timestamp": "2025-12-10T10:31:12.456Z",
    "path": "/etc/passwd",
    "reason": "Path not in allowed directories"
}
```

**Execution:**
```python
{
    "event": "execution",
    "timestamp": "2025-12-10T10:32:00.789Z",
    "tool": "sed_substitute",
    "operation": "in-place edit",
    "path": "/tmp/test.txt",
    "success": true
}
```

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Testing Requirements

### 7.1 Unit Tests

```python
def test_validation_failure_logging(caplog):
    """Validation failures should be logged at WARNING level."""
    logger = AuditLogger()
    
    logger.log_validation_failure(
        tool="sed_substitute",
        reason="Forbidden command",
        details={"pattern": "s/a/b/e"}
    )
    
    assert "Validation failure" in caplog.text
    assert "sed_substitute" in caplog.text
    assert caplog.records[0].levelname == "WARNING"

def test_sanitization():
    """Long strings should be truncated."""
    logger = AuditLogger()
    
    long_string = "a" * 300
    sanitized = logger._sanitize(long_string)
    
    assert len(sanitized) <= 220  # 200 + "[truncated]"
    assert sanitized.endswith("[truncated]")

def test_nested_sanitization():
    """Nested structures should be sanitized recursively."""
    logger = AuditLogger()
    
    data = {
        "pattern": "a" * 300,
        "details": {
            "file": "b" * 300
        }
    }
    
    sanitized = logger._sanitize(data)
    
    assert sanitized["pattern"].endswith("[truncated]")
    assert sanitized["details"]["file"].endswith("[truncated]")

def test_logging_never_raises():
    """Logging failures should not raise exceptions."""
    logger = AuditLogger()
    
    # Pass invalid data that might cause logging errors
    logger.log_validation_failure(
        tool="test",
        reason="test",
        details={"obj": object()}  # Non-serializable
    )
    
    # Should not raise

def test_access_violation_logging(caplog):
    """Access violations should be logged at WARNING level."""
    logger = AuditLogger()
    
    logger.log_access_violation(
        path="/etc/passwd",
        reason="Not in whitelist"
    )
    
    assert "Access violation" in caplog.text
    assert caplog.records[0].levelname == "WARNING"

def test_execution_logging(caplog):
    """Successful executions should log at INFO level."""
    logger = AuditLogger()
    
    logger.log_execution(
        tool="sed_substitute",
        operation="edit",
        path="/tmp/file.txt",
        success=True
    )
    
    assert caplog.records[0].levelname == "INFO"
    
def test_execution_failure_logging(caplog):
    """Failed executions should log at ERROR level."""
    logger = AuditLogger()
    
    logger.log_execution(
        tool="sed_substitute",
        operation="edit",
        path="/tmp/file.txt",
        success=False
    )
    
    assert caplog.records[0].levelname == "ERROR"
```

### 7.2 Integration Tests

**Scenarios:**
1. Tools log all security events
2. Logs contain sufficient context for analysis
3. Sensitive data properly sanitized

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
