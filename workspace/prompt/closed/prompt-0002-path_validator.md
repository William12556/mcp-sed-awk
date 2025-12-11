# T04 Prompt: PathValidator Component

```yaml
prompt_info:
  id: "prompt-0002"
  task_type: "code_generation"
  source_ref: "design-0001-component_security_path"
  date: "2025-12-10"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

context:
  purpose: "Enforce directory whitelist for file access with TOCTOU-resistant path validation"
  integration: "Security domain component; called by all tools before file operations"
  knowledge_references: []
  constraints:
    - "Must be thread-safe for concurrent validation"
    - "Must resolve symlinks to prevent bypass"
    - "Immutable whitelist after initialization"

specification:
  description: |
    Create PathValidator class that enforces directory whitelist access control.
    Validates file paths against allowed directories with path canonicalization,
    symlink resolution, and TOCTOU prevention.
  
  requirements:
    functional:
      - "Initialize with list of allowed directories"
      - "Validate paths are within allowed directories"
      - "Resolve paths to canonical absolute form"
      - "Follow symlinks to actual targets"
      - "Detect and reject path traversal attempts (..)"
      - "Return list of allowed directories"
      - "Reject empty whitelist at initialization"
      - "Validate all whitelist entries are directories at initialization"
    
    technical:
      language: "Python"
      version: "3.10+"
      standards:
        - "Thread-safe implementation"
        - "Comprehensive error handling with SecurityError exception"
        - "Debug logging with traceback"
        - "Professional docstrings (Google style)"
        - "Type hints for all methods"

  performance:
    - target: "O(1) whitelist lookup"
      metric: "complexity"

design:
  architecture: "Class-based validator with immutable set of canonical paths"
  
  components:
    - name: "PathValidator"
      type: "class"
      purpose: "Validate file paths against directory whitelist"
      interface:
        inputs:
          - name: "allowed_directories"
            type: "List[str]"
            description: "List of directory paths to allow"
        outputs:
          type: "PathValidator"
          description: "Initialized validator instance"
        raises:
          - "ValueError: Empty whitelist or invalid directory"
      logic:
        - "__init__: canonicalize directories, verify exist, store as set"
        - "validate_path: resolve input path, check if subpath of any allowed"
        - "list_allowed: return sorted list of allowed directories"
        - "_canonicalize: resolve to absolute path, follow symlinks"
        - "_is_subpath: check if path is within allowed directory tree"
    
    - name: "SecurityError"
      type: "class"
      purpose: "Custom exception for path access violations"
      interface:
        inputs:
          - name: "message"
            type: "str"
            description: "Human-readable error"
          - name: "path"
            type: "Optional[str]"
            description: "Path that violated access"
        outputs:
          type: "Exception"
          description: "Raised security error"
      logic:
        - "Store message and path as attributes"
        - "Inherit from base Exception"
  
  dependencies:
    internal: []
    external:
      - "pathlib (standard library)"
      - "typing (standard library)"

data_schema:
  entities:
    - name: "PathValidator"
      attributes:
        - name: "_allowed_dirs"
          type: "Set[Path]"
          constraints: "Immutable after init, canonical paths"
      validation:
        - "All paths in _allowed_dirs must be absolute"
        - "All paths must exist and be directories"
        - "Set must not be empty"

error_handling:
  strategy: "Raise SecurityError for access violations, ValueError for configuration errors"
  exceptions:
    - exception: "ValueError"
      condition: "Empty allowed_directories list"
      handling: "Raise with message 'cannot be empty'"
    - exception: "ValueError"
      condition: "Invalid directory in allowed_directories"
      handling: "Raise with message 'Invalid directory'"
    - exception: "ValueError"
      condition: "File path provided instead of directory"
      handling: "Raise with message 'Not a directory'"
    - exception: "SecurityError"
      condition: "Path outside allowed directories"
      handling: "Raise with message 'Access denied: path not in allowed directories'"
  logging:
    level: "DEBUG"
    format: "{timestamp} {level} PathValidator {method} path={path} allowed={allowed}"

testing:
  unit_tests:
    - scenario: "Valid path in allowed directory"
      expected: "Return canonical Path object"
    - scenario: "Path traversal with ../"
      expected: "SecurityError raised"
    - scenario: "Symlink to forbidden location"
      expected: "SecurityError raised"
    - scenario: "Empty whitelist"
      expected: "ValueError raised at init"
    - scenario: "Invalid directory in whitelist"
      expected: "ValueError raised at init"
    - scenario: "File as allowed directory"
      expected: "ValueError raised at init"
  edge_cases:
    - "Relative paths (should resolve to absolute)"
    - "Trailing slashes in directory paths"
    - "Case sensitivity (platform-dependent)"
    - "Unicode characters in paths"
  validation:
    - "All public methods have docstrings"
    - "All methods have type hints"
    - "Logging present for validation failures"

deliverable:
  format_requirements:
    - "Save generated code directly to specified path"
  files:
    - path: "src/sed_awk_mcp/security/path_validator.py"
      content: |
        Complete implementation with:
        - SecurityError exception class
        - PathValidator class with all methods
        - Path canonicalization logic
        - Subpath checking logic
        - Comprehensive error messages

success_criteria:
  - "Path traversal attempts blocked"
  - "Symlinks resolved and validated"
  - "Whitelist immutable after initialization"
  - "TOCTOU-resistant validation"
  - "Thread-safe implementation"
  - "Code passes type checking"

notes: |
  Critical security boundary. Must prevent all bypass attempts including:
  - Path traversal (../)
  - Symlink redirection
  - Relative path tricks
  - Case variations (platform-dependent)
  
  Canonicalization process:
  1. Convert to Path object
  2. Call .resolve() to get absolute path and follow symlinks
  3. Check if resolved path starts with any allowed directory
  
  TOCTOU prevention: Always use resolved path for actual operations

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
