# T04 Prompt: SecurityValidator Component

```yaml
prompt_info:
  id: "prompt-0001"
  task_type: "code_generation"
  source_ref: "design-0001-component_security_validator"
  date: "2025-12-10"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

context:
  purpose: "Implement input validation for sed patterns and AWK programs to prevent security threats"
  integration: "Foundation component for security domain; called by all tool implementations before execution"
  knowledge_references: []
  constraints:
    - "Must be thread-safe for concurrent validation calls"
    - "Must use frozenset for blacklists (immutable, O(1) lookup)"
    - "No dependencies on other project components"

specification:
  description: |
    Create SecurityValidator class that validates sed patterns, sed programs, and AWK programs
    against command injection, ReDoS, and forbidden operations. Implements defense-in-depth
    through multiple validation layers.
  
  requirements:
    functional:
      - "Validate sed patterns with length, blacklist, metacharacter, and complexity checks"
      - "Validate multi-line sed programs line-by-line"
      - "Validate AWK programs with length, blacklist, and metacharacter checks"
      - "Detect ReDoS patterns (nested quantifiers, excessive repetition)"
      - "Reject patterns containing shell metacharacters"
      - "Reject patterns containing blacklisted sed commands (e, r, w, q, Q, R, W, T, t, b, :)"
      - "Reject AWK programs containing blacklisted functions (system, popen, getline, close, fflush)"
    
    technical:
      language: "Python"
      version: "3.10+"
      standards:
        - "Thread-safe implementation (no mutable shared state)"
        - "Comprehensive error handling with ValidationError exception"
        - "Debug logging with traceback on validation failures"
        - "Professional docstrings (Google style)"
        - "Type hints for all methods"

  performance:
    - target: "<10ms validation time"
      metric: "time"
    - target: "O(1) blacklist lookup"
      metric: "complexity"

design:
  architecture: "Class-based validator with frozen constants and compiled regex patterns"
  
  components:
    - name: "SecurityValidator"
      type: "class"
      purpose: "Validate sed/AWK inputs against security threats"
      interface:
        inputs:
          - name: "pattern"
            type: "str"
            description: "Sed pattern or AWK program to validate"
        outputs:
          type: "None"
          description: "Raises ValidationError on failure, returns None on success"
        raises:
          - "ValidationError: Input failed validation with specific reason"
      logic:
        - "Initialize with class constants (blacklists, limits)"
        - "Compile ReDoS detection patterns on initialization"
        - "validate_sed_pattern: length → blacklist → metachar → complexity checks"
        - "validate_sed_program: length → line-by-line blacklist → metachar checks"
        - "validate_awk_program: length → blacklist → metachar checks"
        - "_check_length: compare against MAX_PATTERN_LENGTH or MAX_PROGRAM_LENGTH"
        - "_check_blacklist: iterate blacklist, check presence in text"
        - "_check_metacharacters: iterate SHELL_METACHARACTERS, check presence"
        - "_check_complexity: detect nested quantifiers, excessive repetition, deep nesting"
        - "_calculate_nesting_depth: count parenthesis depth"
    
    - name: "ValidationError"
      type: "class"
      purpose: "Custom exception for validation failures"
      interface:
        inputs:
          - name: "message"
            type: "str"
            description: "Human-readable error"
          - name: "reason"
            type: "str"
            description: "Machine-readable code"
          - name: "details"
            type: "Optional[Dict[str, Any]]"
            description: "Additional context"
        outputs:
          type: "Exception"
          description: "Raised validation error"
      logic:
        - "Store message, reason, details as attributes"
        - "Inherit from base Exception class"
  
  dependencies:
    internal: []
    external:
      - "re (standard library)"
      - "typing (standard library)"

data_schema:
  entities:
    - name: "SecurityValidator"
      attributes:
        - name: "SED_BLACKLIST"
          type: "frozenset[str]"
          constraints: "Class constant, immutable"
        - name: "AWK_BLACKLIST"
          type: "frozenset[str]"
          constraints: "Class constant, immutable"
        - name: "SHELL_METACHARACTERS"
          type: "frozenset[str]"
          constraints: "Class constant, immutable"
        - name: "MAX_PATTERN_LENGTH"
          type: "int"
          constraints: "1000"
        - name: "MAX_PROGRAM_LENGTH"
          type: "int"
          constraints: "2000"
        - name: "MAX_NESTING_DEPTH"
          type: "int"
          constraints: "5"
        - name: "MAX_REPETITION_LENGTH"
          type: "int"
          constraints: "100"
        - name: "_redos_patterns"
          type: "List[re.Pattern]"
          constraints: "Compiled regex patterns"
      validation:
        - "Blacklists must be frozenset for immutability and performance"
        - "All constants defined at class level"

error_handling:
  strategy: "Raise ValidationError with descriptive messages for all validation failures"
  exceptions:
    - exception: "ValidationError"
      condition: "Pattern exceeds length limit"
      handling: "Raise with message indicating max length"
    - exception: "ValidationError"
      condition: "Blacklisted command/function detected"
      handling: "Raise with message indicating forbidden item"
    - exception: "ValidationError"
      condition: "Shell metacharacter detected"
      handling: "Raise with message indicating character"
    - exception: "ValidationError"
      condition: "ReDoS pattern detected"
      handling: "Raise with message indicating issue type"
  logging:
    level: "DEBUG"
    format: "{timestamp} {level} SecurityValidator {method} pattern={pattern[:100]} error={error}"

testing:
  unit_tests:
    - scenario: "Valid sed pattern 's/old/new/g'"
      expected: "No exception raised"
    - scenario: "Pattern with 'e' command"
      expected: "ValidationError raised with 'Forbidden' message"
    - scenario: "Pattern with nested quantifiers '(a+)+'"
      expected: "ValidationError raised with 'ReDoS' message"
    - scenario: "Pattern exceeding 1000 chars"
      expected: "ValidationError raised with 'length' message"
    - scenario: "Pattern with semicolon ';'"
      expected: "ValidationError raised with 'metacharacter' message"
    - scenario: "AWK program with system() call"
      expected: "ValidationError raised with 'Forbidden' message"
  edge_cases:
    - "Empty string input"
    - "Pattern at exactly max length"
    - "Multiple validation failures (report first)"
    - "Unicode characters in patterns"
  validation:
    - "All public methods have docstrings"
    - "All methods have type hints"
    - "Logging present for all validation failures"

deliverable:
  format_requirements:
    - "Save generated code directly to specified path"
    - "Include comprehensive docstrings"
    - "Include type hints"
  files:
    - path: "src/sed_awk_mcp/security/validator.py"
      content: |
        Complete implementation with:
        - ValidationError exception class
        - SecurityValidator class with all methods
        - Class constants (blacklists, limits)
        - ReDoS detection logic
        - Comprehensive error messages

success_criteria:
  - "All validation methods correctly detect forbidden patterns"
  - "Thread-safe implementation (no mutable class attributes)"
  - "ValidationError raised with descriptive messages"
  - "Blacklist lookups use frozenset"
  - "ReDoS detection prevents nested quantifiers and excessive repetition"
  - "Code passes type checking (mypy compatible)"

notes: |
  Security-critical component. Validation must be comprehensive but not overly restrictive.
  Balance security with usability - legitimate patterns should pass validation.
  
  Blacklist rationale:
  - Sed 'e' command executes arbitrary shell commands
  - Sed 'r'/'w' commands bypass path validation
  - Sed control flow commands enable complex exploits
  - AWK system/popen execute arbitrary commands
  - AWK getline bypasses input control

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
