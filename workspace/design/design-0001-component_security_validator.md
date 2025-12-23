Created: 2025 December 10

# Component Design: SecurityValidator

## Document Information

**Document ID:** design-0001-component_security_validator
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

**Component Name:** SecurityValidator

**Purpose:** Validate sed patterns/programs and AWK programs against security threats including command injection, ReDoS, and forbidden operations.

**Responsibilities:**
- Pattern syntax validation
- Command blacklist enforcement
- Complexity analysis (ReDoS detection)
- Shell metacharacter filtering
- Length limit enforcement

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation Details

### 2.1 Class Definition

```python
class SecurityValidator:
    """Validates sed/AWK inputs against security threats."""
    
    # Class constants
    SED_BLACKLIST = frozenset({'e', 'r', 'w', 'q', 'Q', 'R', 'W', 'T', 't', 'b', ':'})
    AWK_BLACKLIST = frozenset({'system', 'popen', 'getline', 'close', 'fflush'})
    SHELL_METACHARACTERS = frozenset({';', '|', '&', '$', '`', '\n', '\r', '\x00'})
    
    MAX_PATTERN_LENGTH = 1000
    MAX_PROGRAM_LENGTH = 2000
    MAX_NESTING_DEPTH = 5
    MAX_REPETITION_LENGTH = 100
    
    def __init__(self) -> None:
        """Initialize validator with compiled regex patterns."""
        self._redos_patterns = self._compile_redos_patterns()
    
    def validate_sed_pattern(self, pattern: str) -> None:
        """Validate sed pattern for substitution commands.
        
        Args:
            pattern: Sed pattern string (e.g., 's/find/replace/g')
            
        Raises:
            ValidationError: If pattern contains forbidden commands,
                           exceeds length limits, or has complexity issues
        """
        
    def validate_sed_program(self, program: str) -> None:
        """Validate multi-line sed program.
        
        Args:
            program: Sed program with multiple commands
            
        Raises:
            ValidationError: If program contains forbidden commands
        """
        
    def validate_awk_program(self, program: str) -> None:
        """Validate AWK program.
        
        Args:
            program: AWK program string
            
        Raises:
            ValidationError: If program contains forbidden functions
        """
```

### 2.2 Key Elements

**Validation Methods:**
- `validate_sed_pattern()` - Single pattern validation
- `validate_sed_program()` - Multi-line program validation
- `validate_awk_program()` - AWK program validation
- `_check_length()` - Length limit enforcement
- `_check_blacklist()` - Forbidden command detection
- `_check_complexity()` - ReDoS pattern detection
- `_check_metacharacters()` - Shell character filtering

**Blacklist Sets:**
```python
# Sed commands that enable execution or I/O
SED_BLACKLIST = {
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
}

# AWK functions that enable system access
AWK_BLACKLIST = {
    'system',   # Execute shell command
    'popen',    # Open pipe to command
    'getline',  # Read from file/command
    'close',    # Close file/pipe
    'fflush'    # Flush output (can be abused)
}
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Interfaces

### 3.1 Public Methods

```python
def validate_sed_pattern(self, pattern: str) -> None:
    """Validate sed pattern.
    
    Validation steps:
    1. Check length (≤1000 chars)
    2. Check for blacklisted commands
    3. Check for shell metacharacters
    4. Check for ReDoS patterns
    
    Args:
        pattern: Sed pattern to validate
        
    Raises:
        ValidationError: With specific reason for failure
    """

def validate_sed_program(self, program: str) -> None:
    """Validate sed program.
    
    Validation steps:
    1. Check length (≤2000 chars)
    2. Check each line for blacklisted commands
    3. Check for shell metacharacters
    
    Args:
        program: Multi-line sed program
        
    Raises:
        ValidationError: With specific reason and line number
    """

def validate_awk_program(self, program: str) -> None:
    """Validate AWK program.
    
    Validation steps:
    1. Check length (≤2000 chars)
    2. Check for blacklisted functions
    3. Check for shell metacharacters
    
    Args:
        program: AWK program string
        
    Raises:
        ValidationError: With specific reason for failure
    """
```

### 3.2 Internal Methods

```python
def _check_length(self, text: str, max_length: int, label: str) -> None:
    """Check text length against limit.
    
    Raises:
        ValidationError: If text exceeds max_length
    """

def _check_blacklist(
    self, 
    text: str, 
    blacklist: frozenset, 
    label: str
) -> None:
    """Check for blacklisted commands/functions.
    
    Raises:
        ValidationError: If blacklisted item found
    """

def _check_metacharacters(self, text: str) -> None:
    """Check for shell metacharacters.
    
    Raises:
        ValidationError: If metacharacter found
    """

def _check_complexity(self, pattern: str) -> None:
    """Analyze pattern complexity for ReDoS.
    
    Detects:
    - Nested quantifiers: (a+)+
    - Overlapping alternations: (a|a)*
    - Excessive repetition: a{1000,}
    
    Raises:
        ValidationError: If dangerous pattern detected
    """

def _compile_redos_patterns(self) -> List[re.Pattern]:
    """Compile regex patterns for ReDoS detection.
    
    Returns:
        List of compiled patterns
    """
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Processing Logic

### 4.1 Sed Pattern Validation

```python
def validate_sed_pattern(self, pattern: str) -> None:
    # Step 1: Length check
    self._check_length(pattern, self.MAX_PATTERN_LENGTH, "Pattern")
    
    # Step 2: Blacklist check
    self._check_blacklist(pattern, self.SED_BLACKLIST, "sed command")
    
    # Step 3: Metacharacter check
    self._check_metacharacters(pattern)
    
    # Step 4: Complexity check (ReDoS)
    self._check_complexity(pattern)
```

**Blacklist Detection:**
```python
def _check_blacklist(self, text: str, blacklist: frozenset, label: str) -> None:
    for item in blacklist:
        if item in text:
            raise ValidationError(
                f"Forbidden {label} detected: '{item}'"
            )
```

### 4.2 ReDoS Detection

```python
def _check_complexity(self, pattern: str) -> None:
    # Check for nested quantifiers
    nested_quantifiers = r'(\(.*[+*]\))[+*]'
    if re.search(nested_quantifiers, pattern):
        raise ValidationError(
            "Pattern contains nested quantifiers (potential ReDoS)"
        )
    
    # Check for excessive repetition
    excessive_rep = r'\{(\d+),?\}' 
    for match in re.finditer(excessive_rep, pattern):
        count = int(match.group(1))
        if count > self.MAX_REPETITION_LENGTH:
            raise ValidationError(
                f"Excessive repetition count: {count} (max: {self.MAX_REPETITION_LENGTH})"
            )
    
    # Check nesting depth
    depth = self._calculate_nesting_depth(pattern)
    if depth > self.MAX_NESTING_DEPTH:
        raise ValidationError(
            f"Pattern nesting depth {depth} exceeds limit {self.MAX_NESTING_DEPTH}"
        )

def _calculate_nesting_depth(self, pattern: str) -> int:
    """Calculate maximum nesting depth of parentheses."""
    max_depth = 0
    current_depth = 0
    
    for char in pattern:
        if char == '(':
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char == ')':
            current_depth = max(0, current_depth - 1)
    
    return max_depth
```

### 4.3 AWK Program Validation

```python
def validate_awk_program(self, program: str) -> None:
    # Step 1: Length check
    self._check_length(program, self.MAX_PROGRAM_LENGTH, "Program")
    
    # Step 2: Blacklist check (function names)
    self._check_blacklist(program, self.AWK_BLACKLIST, "AWK function")
    
    # Step 3: Metacharacter check
    self._check_metacharacters(program)
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Error Handling

### 5.1 Exception Hierarchy

```python
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
    ):
        super().__init__(message)
        self.message = message
        self.reason = reason
        self.details = details or {}
```

### 5.2 Error Messages

**Pattern-specific:**
```python
# Length violation
"Pattern exceeds maximum length of 1000 characters"

# Blacklist violation
"Forbidden sed command detected: 'e'"

# Metacharacter violation
"Pattern contains forbidden shell metacharacter: ';'"

# Complexity violation
"Pattern contains nested quantifiers (potential ReDoS)"
```

**Program-specific:**
```python
# AWK blacklist
"Forbidden AWK function detected: 'system'"

# Multi-line sed
"Line 5: Forbidden sed command detected: 'w'"
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Data Structures

### 6.1 Validation Constants

```python
# Frozen sets (immutable, optimized lookup)
SED_BLACKLIST: frozenset[str]
AWK_BLACKLIST: frozenset[str]
SHELL_METACHARACTERS: frozenset[str]

# Numeric limits
MAX_PATTERN_LENGTH: int = 1000
MAX_PROGRAM_LENGTH: int = 2000
MAX_NESTING_DEPTH: int = 5
MAX_REPETITION_LENGTH: int = 100
```

### 6.2 ReDoS Patterns

```python
_redos_patterns: List[re.Pattern] = [
    re.compile(r'(\(.*[+*]\))[+*]'),  # Nested quantifiers
    re.compile(r'(\([^)]*\|[^)]*\))[*+]'),  # Alternation with quantifier
    re.compile(r'\{(\d+),?\}'),  # Explicit repetition
]
```

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Testing Requirements

### 7.1 Unit Tests

**Test Categories:**
1. Valid inputs (should pass)
2. Blacklisted commands (should raise ValidationError)
3. Length violations (should raise ValidationError)
4. ReDoS patterns (should raise ValidationError)
5. Metacharacter violations (should raise ValidationError)

**Test Cases:**

```python
def test_valid_sed_pattern():
    """Valid sed patterns should pass validation."""
    validator = SecurityValidator()
    
    # Basic substitution
    validator.validate_sed_pattern('s/old/new/')
    
    # With flags
    validator.validate_sed_pattern('s/old/new/g')
    
    # With line range
    validator.validate_sed_pattern('1,10s/old/new/')

def test_sed_blacklist_detection():
    """Blacklisted commands should be rejected."""
    validator = SecurityValidator()
    
    # Execute command
    with pytest.raises(ValidationError, match="Forbidden.*'e'"):
        validator.validate_sed_pattern('s/old/new/e')
    
    # Write command
    with pytest.raises(ValidationError, match="Forbidden.*'w'"):
        validator.validate_sed_pattern('w output.txt')

def test_redos_detection():
    """ReDoS patterns should be rejected."""
    validator = SecurityValidator()
    
    # Nested quantifiers
    with pytest.raises(ValidationError, match="nested quantifiers"):
        validator.validate_sed_pattern('(a+)+')
    
    # Excessive repetition
    with pytest.raises(ValidationError, match="Excessive repetition"):
        validator.validate_sed_pattern('a{10000}')

def test_metacharacter_detection():
    """Shell metacharacters should be rejected."""
    validator = SecurityValidator()
    
    # Semicolon
    with pytest.raises(ValidationError, match="metacharacter"):
        validator.validate_sed_pattern('s/old/new/; rm -rf /')
    
    # Pipe
    with pytest.raises(ValidationError, match="metacharacter"):
        validator.validate_sed_pattern('s/old/new/ | cat')

def test_length_limits():
    """Patterns exceeding length limits should be rejected."""
    validator = SecurityValidator()
    
    # Pattern too long
    long_pattern = 's/' + 'a' * 1000 + '/new/'
    with pytest.raises(ValidationError, match="exceeds maximum length"):
        validator.validate_sed_pattern(long_pattern)

def test_awk_validation():
    """AWK program validation."""
    validator = SecurityValidator()
    
    # Valid program
    validator.validate_awk_program('{print $1}')
    
    # Forbidden function
    with pytest.raises(ValidationError, match="Forbidden.*'system'"):
        validator.validate_awk_program('{system("ls")}')
```

### 7.2 Integration Tests

**Scenarios:**
1. Tools Domain calls validator before execution
2. Multiple validation failures captured
3. Error messages propagate correctly

### 7.3 Performance Tests

**Requirements:**
- Validation completes in <10ms for typical patterns
- Blacklist lookup: O(1) using frozenset
- ReDoS detection: Linear scan acceptable for pattern length limits

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description               |
| ------- | ---------- | ------------------------- |
| 1.0     | 2025-12-10 | Initial component design  |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
