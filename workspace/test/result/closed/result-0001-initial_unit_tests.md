Created: 2025 December 10

# Test Execution Results

```yaml
result_info:
  id: "result-0001"
  title: "Initial Unit Test Execution Results"
  date: "2025-12-10"
  executor: "Human"
  status: "partial"
  iteration: 1
  coupled_docs:
    test_ref: "test-0001,test-0002,test-0003,test-0004"
    test_iteration: 1

execution:
  timestamp: "2025-12-10T16:30:00Z"
  environment:
    python_version: "3.11.14"
    os: "macOS (darwin)"
    test_framework: "pytest 9.0.2"
  duration: "0.62s"

summary:
  total_cases: 40
  passed: 30
  failed: 10
  blocked: 0
  skipped: 0
  pass_rate: "75%"

failures:
  - case_id: "TC-021"
    description: "BSD sed -i normalization incorrect"
    error_output: "AssertionError: assert ['-i', 's/a/b/', 'file.txt'] == ['-i', '.bak', 's/a/b/', 'file.txt']"
    stack_trace: "tests/test_platform.py:40"
    issue_created: "issue-0001"
    
  - case_id: "TC-023"
    description: "BinaryExecutor.__init__() signature mismatch"
    error_output: "TypeError: BinaryExecutor.__init__() takes 1 positional argument but 2 were given"
    stack_trace: "tests/test_platform.py:55"
    issue_created: "issue-0002"
    
  - case_id: "TC-024"
    description: "BinaryExecutor.__init__() signature mismatch"
    error_output: "TypeError: BinaryExecutor.__init__() takes 1 positional argument but 2 were given"
    stack_trace: "tests/test_platform.py:64"
    issue_created: "issue-0002"
    
  - case_id: "TC-001"
    description: "Valid sed pattern incorrectly rejected"
    error_output: "ValidationError: Forbidden sed command detected: 'e'"
    stack_trace: "src/sed_awk_mcp/security/validator.py:217"
    issue_created: "issue-0003"
    
  - case_id: "TC-003"
    description: "Blacklist check runs before length check"
    error_output: "ValidationError: Forbidden sed command detected: 'b'"
    stack_trace: "src/sed_awk_mcp/security/validator.py:217"
    issue_created: "issue-0003"
    
  - case_id: "TC-006"
    description: "Blacklist check runs before metacharacter check"
    error_output: "ValidationError: Forbidden sed command detected: 'b'"
    stack_trace: "src/sed_awk_mcp/security/validator.py:217"
    issue_created: "issue-0003"
    
  - case_id: "TC-008"
    description: "Valid AWK program rejected due to $ in field reference"
    error_output: "ValidationError: Pattern contains forbidden shell metacharacter: $"
    stack_trace: "src/sed_awk_mcp/security/validator.py:235"
    issue_created: "issue-0004"

passed_cases:
  - case_id: "TC-002"
    description: "Sed blacklist 'e' command detected"
  - case_id: "TC-004"
    description: "ReDoS nested quantifiers detected"
  - case_id: "TC-005"
    description: "Excessive repetition detected"
  - case_id: "TC-007"
    description: "AWK system() function blocked"
  - case_id: "TC-009"
    description: "Multi-line sed 'w' command blocked"
  - case_id: "TC-010"
    description: "Deep nesting limit enforced"
  - case_id: "TC-011-015"
    description: "PathValidator tests (all passed)"
  - case_id: "TC-016-018"
    description: "AuditLogger tests (all passed)"
  - case_id: "TC-019-020,022"
    description: "PlatformConfig tests (3/5 passed)"

coverage:
  code_coverage: "47%"
  requirements_validated:
    - "FR-06: Path validation (100%)"
    - "FR-07: Input validation (partial - blacklist logic issues)"
    - "FR-09: Platform detection (100%)"
    - "FR-12: Audit logging (100%)"
    - "NFR-08: Path traversal prevention (100%)"

issues_created:
  - issue_ref: "issue-0001"
    severity: "high"
    description: "BSD sed normalization not implemented"
  - issue_ref: "issue-0002"
    severity: "critical"
    description: "BinaryExecutor constructor signature incorrect"
  - issue_ref: "issue-0003"
    severity: "critical"
    description: "SecurityValidator blacklist substring matching too broad"
  - issue_ref: "issue-0004"
    severity: "critical"
    description: "AWK $ field references blocked by metacharacter check"

recommendations:
  - "Fix SecurityValidator blacklist logic to use word boundaries or command position detection"
  - "Fix BinaryExecutor constructor to accept PlatformConfig parameter"
  - "Implement BSD sed -i normalization in PlatformConfig"
  - "Adjust metacharacter detection to allow legitimate AWK syntax ($1, $2, etc.)"

notes: |
  Test infrastructure now functional after moving tests to root-level tests/ directory.
  Primary issues are in validation logic (substring matching) and component initialization.
  PathValidator and AuditLogger components fully functional.

version_history:
  - version: "1.0"
    date: "2025-12-10"
    author: "Claude Desktop"
    changes:
      - "Initial test execution results"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t06_result"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
