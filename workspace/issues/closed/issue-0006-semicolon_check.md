Created: 2025 December 10

# Issue: Semicolon Metacharacter Not Validated

```yaml
issue_info:
  id: "issue-0006"
  title: "Semicolon metacharacter check bypassed in sed patterns"
  date: "2025-12-10"
  status: "open"
  severity: "high"
  type: "defect"
  iteration: 1

source:
  origin: "test_result"
  test_ref: "test-0001"
  description: "TC-006: 's/a/b/; rm -rf /' not rejected for semicolon"

affected_scope:
  components:
    - name: "SecurityValidator"
      file_path: "src/sed_awk_mcp/security/validator.py"

reproduction:
  steps:
    - "validator.validate_sed_pattern('s/a/b/; rm -rf /')"
  error_output: "Forbidden sed command detected: 'r' (should be metacharacter)"

behavior:
  expected: "Reject due to semicolon metacharacter"
  actual: "Parser includes '; rm -rf /' as flags, triggers 'r' blacklist instead"

analysis:
  root_cause: "_check_sed_pattern_structure parses entire string after s/pattern/replacement/ as flags, including shell commands after semicolon"
  technical_notes: "Need metacharacter check before structure parsing"

resolution:
  approach: "Add _check_metacharacters() call before _check_sed_pattern_structure()"

metadata:
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
