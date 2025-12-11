# T04 Prompt: AuditLogger Component

```yaml
prompt_info:
  id: "prompt-0003"
  task_type: "code_generation"
  source_ref: "design-0001-component_security_audit"
  date: "2025-12-10"
  priority: "medium"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

context:
  purpose: "Provide audit logging for security-relevant events"
  integration: "Security domain component; called by tools after validation and execution"
  knowledge_references: []
  constraints:
    - "Must never raise exceptions (graceful degradation)"
    - "Must sanitize sensitive data before logging"
    - "Thread-safe for concurrent logging"

specification:
  description: |
    Create AuditLogger class that logs security-relevant events including validation
    failures, access violations, and tool executions. Implements fail-safe logging
    with automatic sanitization and structured output.
  
  requirements:
    functional:
      - "Log validation failures at WARNING level"
      - "Log access violations at WARNING level"
      - "Log successful executions at INFO level"
      - "Log failed executions at ERROR level"
      - "Sanitize long strings (truncate to 200 chars)"
      - "Sanitize nested data structures recursively"
      - "Include ISO 8601 timestamps (UTC)"
      - "Never raise exceptions from logging methods"
      - "Fallback to stderr if logging fails"
    
    technical:
      language: "Python"
      version: "3.10+"
      standards:
        - "Thread-safe implementation"
        - "Comprehensive error handling with silent failure"
        - "Professional docstrings (Google style)"
        - "Type hints for all methods"

design:
  architecture: "Class-based logger with Python logging integration"
  
  components:
    - name: "AuditLogger"
      type: "class"
      purpose: "Log security events with sanitization"
      interface:
        inputs:
          - name: "tool"
            type: "str"
            description: "Tool name (optional)"
          - name: "reason"
            type: "str"
            description: "Event reason (optional)"
          - name: "path"
            type: "str"
            description: "File path (optional)"
          - name: "details"
            type: "Dict[str, Any]"
            description: "Additional context (optional)"
        outputs:
          type: "None"
          description: "No return value"
        raises:
          - "None (exceptions caught internally)"
      logic:
        - "__init__: get logger instance named 'sed_awk_mcp.audit'"
        - "log_validation_failure: sanitize details, log at WARNING"
        - "log_access_violation: sanitize path, log at WARNING"
        - "log_execution: sanitize details, log at INFO/ERROR based on success"
        - "_sanitize: recursively truncate strings > 200 chars"
        - "_get_timestamp: return current UTC time as ISO 8601"
  
  dependencies:
    internal: []
    external:
      - "logging (standard library)"
      - "datetime (standard library)"
      - "sys (standard library)"
      - "typing (standard library)"

data_schema:
  entities:
    - name: "LogEvent"
      attributes:
        - name: "event"
          type: "str"
          constraints: "validation_failure, access_violation, execution"
        - name: "timestamp"
          type: "str"
          constraints: "ISO 8601 UTC format"
        - name: "tool"
          type: "Optional[str]"
          constraints: "Tool name if applicable"
        - name: "reason"
          type: "Optional[str]"
          constraints: "Event reason/error message"
        - name: "path"
          type: "Optional[str]"
          constraints: "Sanitized file path"
        - name: "details"
          type: "Optional[Dict]"
          constraints: "Sanitized additional context"
        - name: "success"
          type: "Optional[bool]"
          constraints: "Execution success (execution events only)"
      validation:
        - "All string values truncated to 200 chars max"
        - "Nested structures sanitized recursively"

error_handling:
  strategy: "Catch all exceptions, fallback to stderr, never raise"
  exceptions:
    - exception: "Any exception in logging"
      condition: "Logging fails for any reason"
      handling: "Print to stderr, return normally"
    - exception: "Any exception in sanitization"
      condition: "Sanitization fails"
      handling: "Return '[sanitization error]' placeholder"
  logging:
    level: "DEBUG"
    format: "{timestamp} {level} {event} {details_json}"

testing:
  unit_tests:
    - scenario: "Log validation failure"
      expected: "WARNING log with sanitized details"
    - scenario: "Log access violation"
      expected: "WARNING log with sanitized path"
    - scenario: "Log successful execution"
      expected: "INFO log with operation details"
    - scenario: "Log failed execution"
      expected: "ERROR log with failure details"
    - scenario: "Sanitize long string (>200 chars)"
      expected: "String truncated with '[truncated]' suffix"
    - scenario: "Sanitize nested dict with long strings"
      expected: "All strings recursively truncated"
  edge_cases:
    - "Non-serializable objects in details (handle gracefully)"
    - "Logging system unavailable (fallback to stderr)"
    - "Concurrent logging from multiple threads"
  validation:
    - "All public methods have docstrings"
    - "All methods have type hints"
    - "No exceptions propagate from any method"

deliverable:
  format_requirements:
    - "Save generated code directly to specified path"
  files:
    - path: "src/sed_awk_mcp/security/audit.py"
      content: |
        Complete implementation with:
        - AuditLogger class with all methods
        - Sanitization logic for strings and nested structures
        - ISO 8601 timestamp generation
        - Exception handling with stderr fallback
        - Structured log output

success_criteria:
  - "Logging never raises exceptions"
  - "Long strings automatically truncated"
  - "Nested structures sanitized recursively"
  - "Timestamps in ISO 8601 UTC format"
  - "Thread-safe logging"
  - "Code passes type checking"

notes: |
  Fail-safe design critical - audit logging must not disrupt operations.
  
  Sanitization rationale:
  - Prevents log injection attacks
  - Protects sensitive data in patterns
  - Keeps log entries manageable size
  
  Truncation format: "text...[truncated]" at 200 chars

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
