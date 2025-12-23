Created: 2025 December 10

# Component Design: BinaryExecutor

## Document Information

**Document ID:** design-0002-component_platform_executor
**Document Type:** Component Design (Tier 3)
**Parent Domain:** [design-0002-domain_platform](<design-0002-domain_platform.md>)
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
6. [Testing Requirements](<#6.0 testing requirements>)

---

## 1.0 Component Information

**Component Name:** BinaryExecutor

**Purpose:** Execute native binaries with timeout enforcement, resource limits, and structured result handling.

**Responsibilities:**
- Subprocess execution (shell=False)
- Timeout enforcement
- Resource limit application (Linux)
- Stdout/stderr capture
- Exit code handling

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation Details

```python
import subprocess
import sys
import resource
from dataclasses import dataclass
from typing import List
import time

@dataclass
class ExecutionResult:
    """Structured subprocess execution result."""
    stdout: str
    stderr: str
    returncode: int
    duration: float
    
    @property
    def success(self) -> bool:
        return self.returncode == 0

class BinaryExecutor:
    """Execute binaries with resource controls."""
    
    DEFAULT_TIMEOUT = 30
    MEMORY_LIMIT_MB = 100
    CPU_TIME_LIMIT = 30
    
    def execute(
        self,
        binary_path: str,
        args: List[str],
        timeout: int = DEFAULT_TIMEOUT,
        apply_limits: bool = True
    ) -> ExecutionResult:
        """Execute binary with resource controls.
        
        Args:
            binary_path: Full path to binary
            args: Argument list (no shell required)
            timeout: Timeout in seconds
            apply_limits: Apply resource limits (Linux only)
            
        Returns:
            ExecutionResult with stdout, stderr, returncode
            
        Raises:
            TimeoutError: If execution exceeds timeout
            ExecutionError: If execution fails unexpectedly
        """
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Interfaces

```python
def execute(
    self,
    binary_path: str,
    args: List[str],
    timeout: int = 30,
    apply_limits: bool = True
) -> ExecutionResult:
    """Execute binary safely.
    
    Safety measures:
    - shell=False (no shell injection)
    - Timeout enforcement
    - Resource limits (Linux)
    - Argument array (no string parsing)
    
    Returns:
        ExecutionResult with structured data
        
    Raises:
        TimeoutError: Timeout exceeded
        ExecutionError: Unexpected failure
    """
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Processing Logic

### 4.1 Execution Flow

```python
def execute(
    self,
    binary_path: str,
    args: List[str],
    timeout: int = DEFAULT_TIMEOUT,
    apply_limits: bool = True
) -> ExecutionResult:
    """Execute binary with controls."""
    
    # Build command array
    cmd = [binary_path] + args
    
    # Prepare kwargs
    kwargs = {
        'capture_output': True,
        'text': True,
        'timeout': timeout,
        'shell': False  # Critical security requirement
    }
    
    # Apply resource limits on Linux
    if apply_limits and sys.platform == 'linux':
        kwargs['preexec_fn'] = self._set_limits
    
    # Execute and time
    start = time.time()
    try:
        result = subprocess.run(cmd, **kwargs)
        duration = time.time() - start
        
        return ExecutionResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            duration=duration
        )
    except subprocess.TimeoutExpired as e:
        duration = time.time() - start
        raise TimeoutError(
            f"Execution exceeded {timeout}s timeout"
        ) from e
    except Exception as e:
        raise ExecutionError(f"Execution failed: {e}") from e
```

### 4.2 Resource Limits (Linux)

```python
def _set_limits(self) -> None:
    """Set resource limits for subprocess (Linux only).
    
    Limits:
    - Memory: 100MB
    - CPU time: 30s
    """
    
    # Memory limit
    memory_bytes = self.MEMORY_LIMIT_MB * 1024 * 1024
    resource.setrlimit(
        resource.RLIMIT_AS,
        (memory_bytes, memory_bytes)
    )
    
    # CPU time limit
    resource.setrlimit(
        resource.RLIMIT_CPU,
        (self.CPU_TIME_LIMIT, self.CPU_TIME_LIMIT)
    )
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Error Handling

```python
class TimeoutError(Exception):
    """Raised when execution exceeds timeout."""

class ExecutionError(Exception):
    """Raised when execution fails unexpectedly."""
```

**Error Scenarios:**

```python
# Timeout exceeded
TimeoutError("Execution exceeded 30s timeout")

# Binary not executable
ExecutionError("Execution failed: [Errno 13] Permission denied")

# Memory limit exceeded (Linux)
# Subprocess killed with signal, captured in returncode
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Testing Requirements

```python
def test_successful_execution():
    """Successful execution returns ExecutionResult."""
    executor = BinaryExecutor()
    
    result = executor.execute('/bin/echo', ['hello'])
    
    assert result.success
    assert result.stdout.strip() == 'hello'
    assert result.returncode == 0

def test_timeout_enforcement():
    """Execution exceeding timeout raises TimeoutError."""
    executor = BinaryExecutor()
    
    # Sleep for 5 seconds with 1 second timeout
    with pytest.raises(TimeoutError):
        executor.execute('/bin/sleep', ['5'], timeout=1)

def test_shell_false():
    """Verify shell=False prevents shell injection."""
    executor = BinaryExecutor()
    
    # Attempt shell metacharacter injection
    result = executor.execute('/bin/echo', ['hello; ls'])
    
    # Should output literal string, not execute ls
    assert result.stdout.strip() == 'hello; ls'

def test_resource_limits_linux(monkeypatch):
    """Resource limits applied on Linux."""
    if sys.platform != 'linux':
        pytest.skip("Linux only test")
    
    executor = BinaryExecutor()
    
    # Mock setrlimit to verify it's called
    called = []
    def mock_setrlimit(resource, limits):
        called.append((resource, limits))
    
    monkeypatch.setattr(resource, 'setrlimit', mock_setrlimit)
    
    executor.execute('/bin/echo', ['test'], apply_limits=True)
    
    # Verify limits were set
    assert len(called) == 2  # Memory + CPU

def test_error_exit_code():
    """Non-zero exit codes captured correctly."""
    executor = BinaryExecutor()
    
    # /bin/false exits with 1
    result = executor.execute('/bin/false', [])
    
    assert not result.success
    assert result.returncode != 0

def test_stderr_capture():
    """Stderr captured in result."""
    executor = BinaryExecutor()
    
    # Command that writes to stderr
    result = executor.execute('/bin/sh', ['-c', 'echo error >&2'])
    
    assert 'error' in result.stderr

def test_execution_duration():
    """Duration measured correctly."""
    executor = BinaryExecutor()
    
    result = executor.execute('/bin/sleep', ['0.1'])
    
    assert 0.1 <= result.duration < 0.3
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
