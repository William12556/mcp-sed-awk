Created: 2025 December 10

# Issue: SecurityValidator Blacklist Substring Matching Too Broad

```yaml
issue_info:
  id: "issue-0003"
  title: "Blacklist check uses substring matching causing false positives"
  date: "2025-12-10"
  status: "open"
  severity: "critical"
  type: "defect"
  iteration: 1

source:
  origin: "test_result"
  test_ref: "test-0001"
  description: "TC-001, TC-003, TC-006, TC-010 failures: Valid patterns rejected"

affected_scope:
  components:
    - name: "SecurityValidator"
      file_path: "src/sed_awk_mcp/security/validator.py"
  designs:
    - design_ref: "design-0001-component_security_validator"

reproduction:
  steps:
    - "validator.validate_sed_pattern('s/old/new/g')"
    - "validator.validate_sed_pattern('s/aaa/b/')"
  frequency: "always"
  error_output: |
    ValidationError: Forbidden sed command detected: 'e'
    ValidationError: Forbidden sed command detected: 'b'

behavior:
  expected: "'s/old/new/g' and 's/aaa/b/' should pass (no forbidden commands)"
  actual: "Rejected because 'new' contains 'e' and '/b/' contains 'b'"
  impact: "Valid sed patterns rejected, breaking core sed functionality"

analysis:
  root_cause: |
    _check_blacklist() uses substring search: `if item in text`
    Blacklist items like 'e', 'w', 'b' match within legitimate patterns.
    
    Example: 's/old/new/g' contains 'e' in replacement text 'new'
    Example: 's/aaa/b/' contains 'b' in replacement text
  technical_notes: |
    Sed commands are positional: 's/pattern/replacement/flags'
    Blacklisted commands like 'e', 'w' only apply as flags, not in pattern/replacement.
    
    Need context-aware parsing or regex-based detection.

resolution:
  approach: |
    Option 1: Parse sed command structure to check only flags position
    Option 2: Use regex to detect commands at boundaries: r'\b[ewrqQRWTtb:]\b'
    Option 3: Validate against complete sed command syntax
    
    Recommended: Regex with word boundaries checking flags position only

verification:
  verification_steps:
    - "Test 's/old/new/g' - should pass"
    - "Test 's/a/b/' - should pass"
    - "Test 's/a/b/e' - should fail (e flag)"
    - "Test patterns with 'e','w','b' in replacement text - should pass"

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

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
