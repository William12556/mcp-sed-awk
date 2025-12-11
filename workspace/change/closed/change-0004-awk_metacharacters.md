Created: 2025 December 10

# Change: Separate AWK Metacharacter Validation

```yaml
change_info:
  id: "change-0004"
  title: "Create AWK-specific metacharacter set excluding $"
  date: "2025-12-10"
  status: "proposed"
  priority: "critical"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0004"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-0004"

scope:
  summary: "Create AWK_METACHARACTERS without $, use for AWK validation"
  affected_components:
    - name: "SecurityValidator"
      file_path: "src/sed_awk_mcp/security/validator.py"
      change_type: "modify"

rational:
  problem_statement: "$ blocks legitimate AWK field references ($1, $2, $NF)"
  proposed_solution: "Separate metacharacter sets: SHELL_METACHARACTERS for sed, AWK_METACHARACTERS without $ for AWK"

technical_details:
  implementation_approach: |
    1. Add AWK_METACHARACTERS = frozenset([';', '|', '&', '`', '\n', '\r', '\x00'])
    2. Modify validate_awk_program() to use AWK_METACHARACTERS
    3. Keep SHELL_METACHARACTERS with $ for sed validation
  code_changes:
    - component: "SecurityValidator"
      functions_affected: ["validate_awk_program", "_check_metacharacters"]

testing_requirements:
  validation_criteria:
    - "TC-008 passes"
    - "'{print $1}' passes"
    - "'{print $NF}' passes"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
