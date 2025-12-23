Created: 2025 December 10

# Change: Add Length and Metacharacter Validation

```yaml
change_info:
  id: "change-0005"
  title: "Add length check and metacharacter validation before structure parsing"
  date: "2025-12-10"
  status: "proposed"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0005,issue-0006"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-0005, issue-0006"

scope:
  summary: "Add validation checks at start of validate_sed_pattern()"
  affected_components:
    - name: "SecurityValidator"
      file_path: "src/sed_awk_mcp/security/validator.py"
      change_type: "modify"

technical_details:
  implementation_approach: |
    In validate_sed_pattern(), add at start:
    1. Check length <= 1000 (NFR-04)
    2. Call _check_metacharacters(pattern)
    3. Then proceed to _check_sed_pattern_structure()

validation_criteria:
  - "TC-003, TC-006 pass"

metadata:
  template_version: "1.0"
  schema_type: "t02_change"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
