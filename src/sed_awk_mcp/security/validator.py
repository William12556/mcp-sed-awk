"""Security validation for sed patterns and AWK programs.

This module provides comprehensive validation against command injection, ReDoS,
and forbidden operations to ensure safe execution of sed and AWK commands.
"""

import re
import logging
from typing import List, Optional, Dict, Any

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails.
    
    Attributes:
        message: Human-readable error description
        reason: Machine-readable error code
        details: Additional context (optional)
    """
    
    def __init__(
        self, 
        message: str, 
        reason: str = "VALIDATION_FAILED",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize ValidationError.
        
        Args:
            message: Human-readable error description
            reason: Machine-readable error code
            details: Additional context (optional)
        """
        super().__init__(message)
        self.message = message
        self.reason = reason
        self.details = details or {}


class SecurityValidator:
    """Validates sed patterns/programs and AWK programs against security threats.
    
    This class provides comprehensive validation including:
    - Pattern syntax validation
    - Command blacklist enforcement
    - Complexity analysis (ReDoS detection)
    - Shell metacharacter filtering
    - Length limit enforcement
    
    Thread-safe implementation with no mutable shared state.
    """
    
    # Class constants - immutable for thread safety and performance
    SED_BLACKLIST = frozenset({
        'e',  # Execute command
        'r',  # Read file
        'w',  # Write file
        'q',  # Quit
        'Q',  # Quit immediately
        'R',  # Read line from file
        'W',  # Write first line to file
        'T',  # Branch on failure (control flow)
        't',  # Branch on success (control flow)
        'b',  # Branch unconditionally (control flow)
        ':'   # Label definition (control flow)
    })
    
    AWK_BLACKLIST = frozenset({
        'system',   # Execute shell command
        'popen',    # Open pipe to command
        'getline',  # Read from file/command
        'close',    # Close file/pipe
        'fflush'    # Flush output (can be abused)
    })
    
    SHELL_METACHARACTERS = frozenset({
        ';', '|', '&', '$', '`', '\n', '\r', '\x00'
    })
    
    MAX_PATTERN_LENGTH = 1000
    MAX_PROGRAM_LENGTH = 2000
    MAX_NESTING_DEPTH = 5
    MAX_REPETITION_LENGTH = 100
    
    def __init__(self) -> None:
        """Initialize validator with compiled regex patterns for ReDoS detection."""
        self._redos_patterns = self._compile_redos_patterns()
    
    def validate_sed_pattern(self, pattern: str) -> None:
        """Validate sed pattern for substitution commands.
        
        Performs comprehensive validation including length checks, blacklist
        enforcement, metacharacter detection, and complexity analysis.
        
        Args:
            pattern: Sed pattern string (e.g., 's/find/replace/g')
            
        Raises:
            ValidationError: If pattern contains forbidden commands,
                           exceeds length limits, or has complexity issues
        """
        try:
            self._check_length(pattern, self.MAX_PATTERN_LENGTH, "Pattern")
            self._check_blacklist(pattern, self.SED_BLACKLIST, "sed command")
            self._check_metacharacters(pattern)
            self._check_complexity(pattern)
            
        except ValidationError as e:
            logger.debug(
                "SecurityValidator validate_sed_pattern pattern=%s error=%s",
                pattern[:100], str(e)
            )
            raise
    
    def validate_sed_program(self, program: str) -> None:
        """Validate multi-line sed program.
        
        Validates each line of a sed program for forbidden commands and
        metacharacters. Provides line-specific error reporting.
        
        Args:
            program: Sed program with multiple commands
            
        Raises:
            ValidationError: If program contains forbidden commands
        """
        try:
            self._check_length(program, self.MAX_PROGRAM_LENGTH, "Program")
            
            lines = program.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        self._check_blacklist(line, self.SED_BLACKLIST, "sed command")
                        self._check_metacharacters(line)
                    except ValidationError as e:
                        raise ValidationError(
                            f"Line {line_num}: {e.message}",
                            e.reason,
                            {**e.details, "line_number": line_num}
                        )
                        
        except ValidationError as e:
            logger.debug(
                "SecurityValidator validate_sed_program program=%s error=%s",
                program[:100], str(e)
            )
            raise
    
    def validate_awk_program(self, program: str) -> None:
        """Validate AWK program.
        
        Validates AWK program against blacklisted functions, metacharacters,
        and length limits.
        
        Args:
            program: AWK program string
            
        Raises:
            ValidationError: If program contains forbidden functions
        """
        try:
            self._check_length(program, self.MAX_PROGRAM_LENGTH, "Program")
            self._check_blacklist(program, self.AWK_BLACKLIST, "AWK function")
            self._check_metacharacters(program)
            
        except ValidationError as e:
            logger.debug(
                "SecurityValidator validate_awk_program program=%s error=%s",
                program[:100], str(e)
            )
            raise
    
    def _check_length(self, text: str, max_length: int, label: str) -> None:
        """Check text length against limit.
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length
            label: Label for error messages
            
        Raises:
            ValidationError: If text exceeds max_length
        """
        if len(text) > max_length:
            raise ValidationError(
                f"{label} exceeds maximum length of {max_length} characters",
                "LENGTH_EXCEEDED",
                {"length": len(text), "max_length": max_length}
            )
    
    def _check_blacklist(
        self, 
        text: str, 
        blacklist: frozenset, 
        label: str
    ) -> None:
        """Check for blacklisted commands/functions.
        
        Uses frozenset for O(1) lookup performance.
        
        Args:
            text: Text to validate
            blacklist: Set of forbidden items
            label: Label for error messages
            
        Raises:
            ValidationError: If blacklisted item found
        """
        for item in blacklist:
            if item in text:
                raise ValidationError(
                    f"Forbidden {label} detected: '{item}'",
                    "BLACKLIST_VIOLATION",
                    {"forbidden_item": item}
                )
    
    def _check_metacharacters(self, text: str) -> None:
        """Check for shell metacharacters.
        
        Args:
            text: Text to validate
            
        Raises:
            ValidationError: If metacharacter found
        """
        for char in self.SHELL_METACHARACTERS:
            if char in text:
                char_repr = repr(char) if char in '\n\r\x00' else char
                raise ValidationError(
                    f"Pattern contains forbidden shell metacharacter: {char_repr}",
                    "METACHARACTER_VIOLATION",
                    {"metacharacter": char}
                )
    
    def _check_complexity(self, pattern: str) -> None:
        """Analyze pattern complexity for ReDoS detection.
        
        Detects multiple types of dangerous patterns:
        - Nested quantifiers: (a+)+
        - Excessive repetition: a{1000,}
        - Deep nesting: ((((a))))
        
        Args:
            pattern: Pattern to analyze
            
        Raises:
            ValidationError: If dangerous pattern detected
        """
        # Check for nested quantifiers using compiled patterns
        for redos_pattern in self._redos_patterns:
            if redos_pattern.search(pattern):
                raise ValidationError(
                    "Pattern contains nested quantifiers (potential ReDoS)",
                    "REDOS_NESTED_QUANTIFIERS"
                )
        
        # Check for excessive repetition
        excessive_rep = re.compile(r'\{(\d+),?\}')
        for match in excessive_rep.finditer(pattern):
            count = int(match.group(1))
            if count > self.MAX_REPETITION_LENGTH:
                raise ValidationError(
                    f"Excessive repetition count: {count} (max: {self.MAX_REPETITION_LENGTH})",
                    "REDOS_EXCESSIVE_REPETITION",
                    {"count": count, "max_count": self.MAX_REPETITION_LENGTH}
                )
        
        # Check nesting depth
        depth = self._calculate_nesting_depth(pattern)
        if depth > self.MAX_NESTING_DEPTH:
            raise ValidationError(
                f"Pattern nesting depth {depth} exceeds limit {self.MAX_NESTING_DEPTH}",
                "REDOS_DEEP_NESTING",
                {"depth": depth, "max_depth": self.MAX_NESTING_DEPTH}
            )
    
    def _calculate_nesting_depth(self, pattern: str) -> int:
        """Calculate maximum nesting depth of parentheses.
        
        Args:
            pattern: Pattern to analyze
            
        Returns:
            Maximum depth of nested parentheses
        """
        max_depth = 0
        current_depth = 0
        
        for char in pattern:
            if char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == ')':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _compile_redos_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for ReDoS detection.
        
        Returns:
            List of compiled patterns for detecting ReDoS vulnerabilities
        """
        patterns = [
            # Nested quantifiers: (a+)+, (a*)*
            r'(\(.*[+*]\))[+*]',
            # Alternation with quantifier: (a|a)*
            r'(\([^)]*\|[^)]*\))[*+]'
        ]
        
        return [re.compile(pattern) for pattern in patterns]