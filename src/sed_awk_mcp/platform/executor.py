"""Binary execution with security controls and resource limits.

This module provides secure subprocess execution with timeout enforcement,
resource limits, and structured result handling for sed, awk, and diff commands.
"""

import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import List, Optional

# Import resource module only if available (Linux/Unix)
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Structured result from subprocess execution.
    
    Attributes:
        stdout: Standard output as string
        stderr: Standard error as string
        returncode: Process exit code
        duration: Execution time in seconds
    """
    stdout: str
    stderr: str
    returncode: int
    duration: float
    
    @property
    def success(self) -> bool:
        """Check if execution was successful.
        
        Returns:
            True if returncode is 0, False otherwise
        """
        return self.returncode == 0


class TimeoutError(Exception):
    """Raised when execution exceeds timeout limit.
    
    Attributes:
        message: Human-readable error description
        timeout: Timeout value in seconds
    """
    
    def __init__(self, message: str, timeout: Optional[float] = None) -> None:
        """Initialize TimeoutError.
        
        Args:
            message: Human-readable error description
            timeout: Timeout value in seconds (optional)
        """
        super().__init__(message)
        self.message = message
        self.timeout = timeout


class ExecutionError(Exception):
    """Raised when execution fails unexpectedly.
    
    Attributes:
        message: Human-readable error description
        binary_path: Path to binary that failed (optional)
    """
    
    def __init__(self, message: str, binary_path: Optional[str] = None) -> None:
        """Initialize ExecutionError.
        
        Args:
            message: Human-readable error description
            binary_path: Path to binary that failed (optional)
        """
        super().__init__(message)
        self.message = message
        self.binary_path = binary_path


class BinaryExecutor:
    """Execute binaries with security controls and resource limits.
    
    This class provides secure subprocess execution with:
    - No shell invocation (shell=False)
    - Timeout enforcement
    - Resource limits (Linux/Unix only)
    - Structured result handling
    - Comprehensive error handling
    
    Thread-safe implementation suitable for concurrent use.
    """
    
    # Class constants for resource limits
    DEFAULT_TIMEOUT = 30
    MEMORY_LIMIT_MB = 100
    CPU_TIME_LIMIT = 30
    
    def __init__(self) -> None:
        """Initialize BinaryExecutor.
        
        Checks platform capabilities for resource limiting.
        """
        self._has_resource_limits = HAS_RESOURCE and sys.platform.startswith('linux')
        
        logger.debug(
            "BinaryExecutor initialized: resource_limits=%s platform=%s",
            self._has_resource_limits, sys.platform
        )
    
    def execute(
        self,
        binary_path: str,
        args: List[str],
        timeout: int = DEFAULT_TIMEOUT,
        apply_limits: bool = True
    ) -> ExecutionResult:
        """Execute binary with security controls and resource limits.
        
        Executes the binary with shell=False to prevent shell injection,
        enforces timeout limits, and optionally applies resource constraints
        on supported platforms.
        
        Args:
            binary_path: Full path to the binary to execute
            args: Argument list (will be passed as separate arguments)
            timeout: Execution timeout in seconds (default: 30)
            apply_limits: Whether to apply resource limits (default: True)
            
        Returns:
            ExecutionResult with stdout, stderr, returncode, and duration
            
        Raises:
            TimeoutError: If execution exceeds timeout
            ExecutionError: If execution fails unexpectedly
        """
        # Build command array - binary path + arguments
        cmd = [binary_path] + args
        
        # Prepare subprocess kwargs
        kwargs = {
            'capture_output': True,
            'text': True,
            'timeout': timeout,
            'shell': False  # Critical security requirement - no shell injection
        }
        
        # Apply resource limits on supported platforms
        if apply_limits and self._has_resource_limits:
            kwargs['preexec_fn'] = self._set_limits
            logger.debug("BinaryExecutor applying resource limits")
        
        # Log execution attempt
        logger.debug(
            "BinaryExecutor executing: binary=%s args=%s timeout=%s",
            binary_path, args, timeout
        )
        
        # Execute subprocess with timing
        start_time = time.time()
        try:
            result = subprocess.run(cmd, **kwargs)
            duration = time.time() - start_time
            
            execution_result = ExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                duration=duration
            )
            
            logger.debug(
                "BinaryExecutor completed: binary=%s returncode=%d duration=%.3fs",
                binary_path, result.returncode, duration
            )
            
            return execution_result
            
        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            
            logger.warning(
                "BinaryExecutor timeout: binary=%s timeout=%s duration=%.3fs",
                binary_path, timeout, duration
            )
            
            raise TimeoutError(
                f"Execution exceeded {timeout}s timeout",
                timeout=timeout
            ) from e
            
        except (OSError, subprocess.SubprocessError) as e:
            duration = time.time() - start_time
            
            logger.error(
                "BinaryExecutor failed: binary=%s error=%s duration=%.3fs",
                binary_path, str(e), duration
            )
            
            raise ExecutionError(
                f"Execution failed: {e}",
                binary_path=binary_path
            ) from e
        
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                "BinaryExecutor unexpected error: binary=%s error=%s duration=%.3fs",
                binary_path, str(e), duration
            )
            
            raise ExecutionError(
                f"Unexpected execution error: {e}",
                binary_path=binary_path
            ) from e
    
    def _set_limits(self) -> None:
        """Set resource limits for subprocess (Linux/Unix only).
        
        This function is called as preexec_fn in subprocess.run() to set
        resource limits before the child process executes the target binary.
        
        Limits applied:
        - Memory (RLIMIT_AS): 100MB virtual memory
        - CPU time (RLIMIT_CPU): 30 seconds of CPU time
        
        Note: This method is only called on platforms where the resource
        module is available (typically Linux/Unix).
        """
        try:
            # Set memory limit (virtual memory)
            memory_bytes = self.MEMORY_LIMIT_MB * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_AS,
                (memory_bytes, memory_bytes)
            )
            
            # Set CPU time limit
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.CPU_TIME_LIMIT, self.CPU_TIME_LIMIT)
            )
            
        except (OSError, AttributeError) as e:
            # Log but don't fail - resource limits are best effort
            # This will be logged from the parent process context
            # since preexec_fn runs in the child process
            pass