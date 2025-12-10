"""Audit logging for security-relevant events.

This module provides fail-safe audit logging with automatic data sanitization
and structured output for security monitoring and compliance.
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Union, List

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.


class AuditLogger:
    """Logs security-relevant events with sanitization.
    
    This class provides fail-safe audit logging for security events including
    validation failures, access violations, and tool executions. Features:
    - Automatic data sanitization to prevent log injection
    - Structured log output with ISO 8601 timestamps
    - Thread-safe logging with exception handling
    - Graceful degradation (never raises exceptions)
    
    All logging methods are designed to never raise exceptions to prevent
    disruption of normal operations.
    """
    
    def __init__(self, logger_name: str = "sed_awk_mcp.audit") -> None:
        """Initialize audit logger.
        
        Args:
            logger_name: Logger name for hierarchy (default: "sed_awk_mcp.audit")
        """
        try:
            self._logger = logging.getLogger(logger_name)
            # Don't set level here - let configuration handle it
        except Exception as e:
            # Fallback to stderr if logger initialization fails
            print(f"Failed to initialize audit logger: {e}", file=sys.stderr)
            self._logger = None
    
    def log_validation_failure(
        self,
        tool: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log input validation failure.
        
        Logs validation failures at WARNING level with sanitized details
        to prevent exposure of potentially sensitive pattern data.
        
        Args:
            tool: Tool name (e.g., "sed_substitute", "awk_program")
            reason: Validation failure reason
            details: Additional context (will be sanitized before logging)
        """
        try:
            sanitized_details = self._sanitize(details) if details else {}
            
            log_data = {
                "event": "validation_failure",
                "timestamp": self._get_timestamp(),
                "tool": self._sanitize(tool),
                "reason": self._sanitize(reason),
                "details": sanitized_details
            }
            
            if self._logger:
                self._logger.warning(
                    "Validation failure: tool=%s reason=%s",
                    tool, reason,
                    extra=log_data
                )
            else:
                self._fallback_log("WARNING", "Validation failure", log_data)
                
        except Exception as e:
            self._handle_logging_error("log_validation_failure", e)
    
    def log_access_violation(
        self,
        path: str,
        reason: str,
        tool: Optional[str] = None
    ) -> None:
        """Log path access control violation.
        
        Logs access violations at WARNING level with sanitized path
        information to protect sensitive directory structures.
        
        Args:
            path: Attempted path (will be sanitized)
            reason: Access denial reason
            tool: Tool that attempted access (optional)
        """
        try:
            log_data = {
                "event": "access_violation",
                "timestamp": self._get_timestamp(),
                "path": self._sanitize(path),
                "reason": self._sanitize(reason)
            }
            
            if tool:
                log_data["tool"] = self._sanitize(tool)
            
            if self._logger:
                self._logger.warning(
                    "Access violation: path=%s reason=%s",
                    path, reason,
                    extra=log_data
                )
            else:
                self._fallback_log("WARNING", "Access violation", log_data)
                
        except Exception as e:
            self._handle_logging_error("log_access_violation", e)
    
    def log_execution(
        self,
        tool: str,
        operation: str,
        path: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log tool execution.
        
        Logs successful executions at INFO level and failures at ERROR level
        with sanitized operation details.
        
        Args:
            tool: Tool name
            operation: Operation performed (e.g., "substitute", "pattern_match")
            path: Target file path (optional, will be sanitized)
            success: Operation success status (default: True)
            details: Additional execution context (optional, will be sanitized)
        """
        try:
            log_data = {
                "event": "execution",
                "timestamp": self._get_timestamp(),
                "tool": self._sanitize(tool),
                "operation": self._sanitize(operation),
                "success": success
            }
            
            if path:
                log_data["path"] = self._sanitize(path)
                
            if details:
                log_data["details"] = self._sanitize(details)
            
            level = logging.INFO if success else logging.ERROR
            level_name = "INFO" if success else "ERROR"
            message = "Tool execution" if success else "Tool execution failed"
            
            if self._logger:
                self._logger.log(
                    level,
                    "%s: tool=%s operation=%s success=%s",
                    message, tool, operation, success,
                    extra=log_data
                )
            else:
                self._fallback_log(level_name, message, log_data)
                
        except Exception as e:
            self._handle_logging_error("log_execution", e)
    
    def _sanitize(self, data: Any) -> Any:
        """Remove sensitive information from log data.
        
        Recursively sanitizes data structures to prevent log injection
        and exposure of sensitive information. Truncates long strings
        and handles nested structures.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data safe for logging
        """
        try:
            if data is None:
                return None
                
            if isinstance(data, str):
                # Truncate long strings to prevent log bloat
                if len(data) > 200:
                    return data[:200] + "...[truncated]"
                return data
            
            if isinstance(data, (int, float, bool)):
                return data
            
            if isinstance(data, dict):
                # Recursively sanitize dict values
                return {
                    str(k): self._sanitize(v) 
                    for k, v in data.items()
                }
            
            if isinstance(data, (list, tuple)):
                # Sanitize sequences, but limit length to prevent log bloat
                sanitized_items = [self._sanitize(item) for item in data[:20]]
                if len(data) > 20:
                    sanitized_items.append("...[truncated]")
                return sanitized_items
            
            # For other types, convert to string and sanitize
            str_repr = str(data)
            if len(str_repr) > 200:
                return str_repr[:200] + "...[truncated]"
            return str_repr
            
        except Exception:
            # Return safe placeholder if sanitization fails
            return "[sanitization error]"
    
    def _get_timestamp(self) -> str:
        """Get current UTC timestamp in ISO 8601 format.
        
        Returns:
            ISO 8601 formatted UTC timestamp
        """
        try:
            return datetime.utcnow().isoformat() + "Z"
        except Exception:
            # Fallback timestamp if datetime fails
            return "[timestamp error]"
    
    def _handle_logging_error(self, method: str, error: Exception) -> None:
        """Handle logging errors by falling back to stderr.
        
        Args:
            method: Method name where error occurred
            error: Exception that occurred
        """
        try:
            print(
                f"Audit logging failed in {method}: {error}",
                file=sys.stderr
            )
        except Exception:
            # If even stderr fails, silently continue
            pass
    
    def _fallback_log(self, level: str, message: str, data: Dict[str, Any]) -> None:
        """Fallback logging to stderr when logger unavailable.
        
        Args:
            level: Log level string
            message: Log message
            data: Log data dictionary
        """
        try:
            print(
                f"{data.get('timestamp', '[no timestamp]')} {level} "
                f"AuditLogger {message} {data}",
                file=sys.stderr
            )
        except Exception:
            # If even stderr fails, silently continue
            pass