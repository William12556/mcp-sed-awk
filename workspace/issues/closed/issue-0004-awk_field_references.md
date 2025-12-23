Created: 2025 December 10

# Issue: AWK Field References Blocked by Metacharacter Check

```yaml
issue_info:
  id: "issue-0004"
  title: "AWK $ field references incorrectly blocked as shell metacharacter"
  date: "2025-12-10"
  status: "open"
  severity: "critical"
  type: "defect"
  iteration: 1

source:
  origin: "test_result"
  test_ref: "test-0001"
  description: "TC-008 failure: Valid AWK program '{print $1}' rejected"

affected_scope:
  components:
    - name: "SecurityValidator"
      file_path: "src/sed_awk_mcp/security/validator.py"

reproduction:
  steps:
    - "validator.validate_awk_program('{print $1}')"
  frequency: "always"
  error_output: |
    ValidationError: Pattern contains forbidden shell metacharacter: $

behavior:
  expected: "'{print $1}' should pass - $ is legitimate AWK syntax for field access"
  actual: "Rejected due to $ being in SHELL_METACHARACTERS"
  impact: "Blocks all AWK field references ($1, $2, $NF, etc.) - breaks core AWK functionality"

analysis:
  root_cause: |
    SHELL_METACHARACTERS includes '$' for shell variable expansion prevention.
    However, '$' is essential AWK syntax for field references.
  technical_notes: |
    AWK field references: $1, $2, $3, $NF, $0
    AWK variables: NR, NF, FILENAME, etc.
    
    Shell metacharacter detection must distinguish:
    - Shell variable expansion: $VAR, ${VAR}
    - AWK field references: $1, $2 (legitimate)

resolution:
  approach: |
    Option 1: Remove $ from SHELL_METACHARACTERS for AWK validation
    Option 2: Context-aware check: allow $<digit> and $NF patterns
    Option 3: Separate metacharacter sets for sed vs AWK
    
    Recommended: Option 3 - AWK_METACHARACTERS without $

verification:
  verification_steps:
    - "Test '{print $1}' - should pass"
    - "Test '{print $NF}' - should pass"
    - "Test patterns with $(...) shell expansion - should fail"

traceability:
  design_refs:
    - "design-0001-component_security_validator"
  test_refs:
    - "test-0001"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
