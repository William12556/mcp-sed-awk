Created: 2025 December 10

# Debug Prompt: Fix SecurityValidator Blacklist Logic

```yaml
prompt_info:
  id: "prompt-0013"
  task_type: "debug"
  source_ref: "change-0003"
  date: "2025-12-10"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0003"
    change_iteration: 1

specification:
  description: "Replace substring matching with sed command structure parsing"
  requirements:
    functional:
      - "Parse sed s/pattern/replacement/flags structure"
      - "Validate blacklist only against flags section"
      - "Allow 'e', 'w', 'b' in pattern/replacement text"

design:
  components:
    - name: "validate_sed_pattern"
      logic:
        - "Use regex to extract flags: r's/(?:[^/]|\\\\/)+/(?:[^/]|\\\\/)+/([a-z]+)?'"
        - "Check blacklist against captured flags group only"
        - "If no flags section, pass validation"

testing:
  unit_tests:
    - scenario: "'s/old/new/g'"
      expected: "Pass (no blacklisted flags)"
    - scenario: "'s/a/b/'"
      expected: "Pass ('b' in replacement, not flag)"
    - scenario: "'s/a/b/e'"
      expected: "Fail ('e' as flag)"

deliverable:
  files:
    - path: "src/sed_awk_mcp/security/validator.py"

success_criteria:
  - "TC-001, TC-003, TC-006, TC-010 pass"

metadata:
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
