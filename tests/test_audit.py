"""Unit tests for AuditLogger component."""

import pytest
import logging
from sed_awk_mcp.security.audit import AuditLogger


class TestAuditLogger:
    """Test suite for AuditLogger."""
    
    def test_validation_failure_logs_warning(self, caplog):
        """TC-016: Validation failure logged at WARNING."""
        logger = AuditLogger()
        
        with caplog.at_level(logging.WARNING):
            logger.log_validation_failure(
                tool="test_tool",
                reason="test reason",
                details={"key": "value"}
            )
        
        assert any(record.levelname == "WARNING" for record in caplog.records)
    
    def test_string_truncation(self):
        """TC-017: Long strings truncated to 200 chars."""
        logger = AuditLogger()
        long_string = "a" * 300
        
        sanitized = logger._sanitize(long_string)
        
        assert len(sanitized) <= 220  # 200 + "[truncated]"
        assert sanitized.endswith("[truncated]")
    
    def test_logging_never_raises(self):
        """TC-018: Logging never raises exceptions."""
        logger = AuditLogger()
        
        # Pass non-serializable object
        logger.log_validation_failure(
            tool="test",
            reason="test",
            details={"obj": object()}
        )
        # Should not raise
    
    def test_nested_sanitization(self):
        """Nested structures sanitized recursively."""
        logger = AuditLogger()
        
        data = {
            "pattern": "a" * 300,
            "nested": {
                "value": "b" * 300
            }
        }
        
        sanitized = logger._sanitize(data)
        assert sanitized["pattern"].endswith("[truncated]")
        assert sanitized["nested"]["value"].endswith("[truncated]")
    
    def test_access_violation_logs_warning(self, caplog):
        """Access violations logged at WARNING."""
        logger = AuditLogger()
        
        with caplog.at_level(logging.WARNING):
            logger.log_access_violation(
                path="/test/path",
                reason="not in whitelist"
            )
        
        assert any("Access violation" in record.message for record in caplog.records)
    
    def test_execution_success_logs_info(self, caplog):
        """Successful executions log at INFO."""
        logger = AuditLogger()
        
        with caplog.at_level(logging.INFO):
            logger.log_execution(
                tool="test_tool",
                operation="test",
                path="/test/path",
                success=True
            )
        
        assert any(record.levelname == "INFO" for record in caplog.records)
    
    def test_execution_failure_logs_error(self, caplog):
        """Failed executions log at ERROR."""
        logger = AuditLogger()
        
        with caplog.at_level(logging.ERROR):
            logger.log_execution(
                tool="test_tool",
                operation="test",
                path="/test/path",
                success=False
            )
        
        assert any(record.levelname == "ERROR" for record in caplog.records)
