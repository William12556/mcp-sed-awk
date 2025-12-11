"""Unit tests for SecurityValidator component."""

import pytest
from sed_awk_mcp.security.validator import SecurityValidator, ValidationError


class TestSecurityValidator:
    """Test suite for SecurityValidator."""
    
    def test_valid_sed_pattern(self):
        """TC-001: Valid sed pattern passes validation."""
        validator = SecurityValidator()
        validator.validate_sed_pattern('s/old/new/g')  # Should not raise
    
    def test_sed_blacklist_e_command(self):
        """TC-002: Sed pattern with 'e' command rejected."""
        validator = SecurityValidator()
        with pytest.raises(ValidationError, match="Forbidden.*'e'"):
            validator.validate_sed_pattern('s/old/new/e')
    
    def test_pattern_length_limit(self):
        """TC-003: Pattern exceeding 1000 chars rejected."""
        validator = SecurityValidator()
        long_pattern = 's/' + 'a' * 995 + '/b/'
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            validator.validate_sed_pattern(long_pattern)
    
    def test_nested_quantifiers_redos(self):
        """TC-004: Pattern with nested quantifiers rejected."""
        validator = SecurityValidator()
        with pytest.raises(ValidationError, match="nested quantifiers"):
            validator.validate_sed_pattern('(a+)+')
    
    def test_excessive_repetition(self):
        """TC-005: Pattern with excessive repetition rejected."""
        validator = SecurityValidator()
        with pytest.raises(ValidationError, match="Excessive repetition"):
            validator.validate_sed_pattern('a{10000}')
    
    def test_semicolon_metacharacter(self):
        """TC-006: Pattern with semicolon metacharacter rejected."""
        validator = SecurityValidator()
        with pytest.raises(ValidationError, match="metacharacter"):
            validator.validate_sed_pattern('s/a/b/; rm -rf /')
    
    def test_awk_system_function(self):
        """TC-007: AWK program with system() rejected."""
        validator = SecurityValidator()
        with pytest.raises(ValidationError, match="Forbidden.*'system'"):
            validator.validate_awk_program('{system("ls")}')
    
    def test_valid_awk_program(self):
        """TC-008: Valid AWK program passes validation."""
        validator = SecurityValidator()
        validator.validate_awk_program('{print $1}')  # Should not raise
    
    def test_multiline_sed_with_w_command(self):
        """TC-009: Multi-line sed program with 'w' command rejected."""
        validator = SecurityValidator()
        program = "s/old/new/\nw output.txt"
        with pytest.raises(ValidationError, match="Line.*Forbidden"):
            validator.validate_sed_program(program)
    
    def test_deep_nesting_limit(self):
        """TC-010: Deep nesting exceeds limit."""
        validator = SecurityValidator()
        deep_pattern = '((((((a))))))'
        with pytest.raises(ValidationError, match="nesting depth"):
            validator.validate_sed_pattern(deep_pattern)
    
    def test_all_sed_blacklist_commands(self):
        """Verify all SED_BLACKLIST commands are rejected."""
        validator = SecurityValidator()
        blacklist_items = ['e', 'r', 'w', 'q', 'Q', 'R', 'W', 'T', 't', 'b', ':']
        
        for cmd in blacklist_items:
            with pytest.raises(ValidationError, match="Forbidden"):
                validator.validate_sed_pattern(f's/a/b/{cmd}')
    
    def test_all_awk_blacklist_functions(self):
        """Verify all AWK_BLACKLIST functions are rejected."""
        validator = SecurityValidator()
        blacklist_funcs = ['system', 'popen', 'getline', 'close', 'fflush']
        
        for func in blacklist_funcs:
            with pytest.raises(ValidationError, match="Forbidden"):
                validator.validate_awk_program(f'{{{func}()}}')
    
    def test_all_shell_metacharacters(self):
        """Verify all SHELL_METACHARACTERS are rejected."""
        validator = SecurityValidator()
        metacharacters = [';', '|', '&', '$', '`', '\n', '\r', '\x00']
        
        for char in metacharacters:
            with pytest.raises(ValidationError, match="metacharacter"):
                validator.validate_sed_pattern(f's/a/b/{char}')
    
    def test_pattern_at_max_length(self):
        """Pattern at exactly 1000 chars should pass."""
        validator = SecurityValidator()
        pattern = 's/' + 'a' * 994 + '/b/'  # Exactly 1000 chars
        validator.validate_sed_pattern(pattern)  # Should not raise
    
    def test_empty_pattern(self):
        """Empty pattern should pass validation."""
        validator = SecurityValidator()
        validator.validate_sed_pattern('')  # Should not raise
    
    def test_validation_error_attributes(self):
        """ValidationError should have expected attributes."""
        validator = SecurityValidator()
        
        try:
            validator.validate_sed_pattern('s/a/b/e')
        except ValidationError as e:
            assert hasattr(e, 'message')
            assert hasattr(e, 'reason')
            assert hasattr(e, 'details')
            assert e.reason == "BLACKLIST_VIOLATION"
