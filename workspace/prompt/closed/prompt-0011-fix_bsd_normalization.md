Created: 2025 December 10

# Debug Prompt: Fix BSD Sed Normalization

```yaml
prompt_info:
  id: "prompt-0011"
  task_type: "debug"
  source_ref: "change-0001"
  date: "2025-12-10"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: "change-0001"
    change_iteration: 1

context:
  purpose: "Fix BSD sed -i flag normalization in PlatformConfig"
  integration: "Platform domain - ensures BSD/macOS compatibility"

specification:
  description: "Implement BSD branch in normalize_sed_args() method"
  requirements:
    functional:
      - "GNU: ['-i', 's/a/b/', 'file.txt'] → ['-i.bak', 's/a/b/', 'file.txt']"
      - "BSD: ['-i', 's/a/b/', 'file.txt'] → ['-i', '.bak', 's/a/b/', 'file.txt']"

design:
  components:
    - name: "normalize_sed_args"
      type: "function"
      logic:
        - "Find index of '-i' in args list"
        - "If is_gnu_sed: modify args[i] to '-i.bak'"
        - "If NOT is_gnu_sed: insert '.bak' at args[i+1]"
        - "Return modified args list"

error_handling:
  strategy: "Preserve original args if '-i' not found"

testing:
  unit_tests:
    - scenario: "BSD sed with -i"
      expected: "['-i', '.bak', 's/a/b/', 'file.txt']"

deliverable:
  files:
    - path: "src/sed_awk_mcp/platform/config.py"

success_criteria:
  - "TC-021 passes"
  - "Both GNU and BSD normalization work correctly"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
