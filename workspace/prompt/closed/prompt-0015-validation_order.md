Created: 2025 December 10

# Debug Prompt: Add Validation Order Checks

```yaml
prompt_info:
  id: "prompt-0015"
  task_type: "debug"
  source_ref: "change-0005"
  date: "2025-12-10"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: "change-0005"
    change_iteration: 1

specification:
  description: "Add length and metacharacter checks before structure parsing"
  requirements:
    functional:
      - "Check pattern length <= 1000 chars"
      - "Call _check_metacharacters() before _check_sed_pattern_structure()"
      - "Preserve existing structure parsing logic"

design:
  components:
    - name: "validate_sed_pattern"
      logic:
        - "if len(pattern) > 1000: raise ValidationError"
        - "self._check_metacharacters(pattern)"
        - "self._check_sed_pattern_structure(pattern)"

deliverable:
  files:
    - path: "src/sed_awk_mcp/security/validator.py"

success_criteria:
  - "TC-003, TC-006 pass"
  - "All 40 tests pass"

metadata:
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
