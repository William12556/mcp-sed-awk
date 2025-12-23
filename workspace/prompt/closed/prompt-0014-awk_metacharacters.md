Created: 2025 December 10

# Debug Prompt: Separate AWK Metacharacter Validation

```yaml
prompt_info:
  id: "prompt-0014"
  task_type: "debug"
  source_ref: "change-0004"
  date: "2025-12-10"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0004"
    change_iteration: 1

specification:
  description: "Create AWK-specific metacharacter set without $"
  requirements:
    functional:
      - "Add AWK_METACHARACTERS = frozenset([';', '|', '&', '`', '\\n', '\\r', '\\x00'])"
      - "Modify validate_awk_program() to use AWK_METACHARACTERS"
      - "Keep SHELL_METACHARACTERS with $ for sed validation"

design:
  components:
    - name: "SecurityValidator"
      logic:
        - "Add AWK_METACHARACTERS constant (no $)"
        - "Update validate_awk_program() to call _check_metacharacters with AWK_METACHARACTERS"
        - "Preserve existing sed validation with SHELL_METACHARACTERS"

deliverable:
  files:
    - path: "src/sed_awk_mcp/security/validator.py"

success_criteria:
  - "TC-008 passes"
  - "'{print $1}' validates successfully"

metadata:
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
