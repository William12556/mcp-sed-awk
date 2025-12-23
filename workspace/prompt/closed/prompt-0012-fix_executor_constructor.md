Created: 2025 December 10

# Debug Prompt: Fix BinaryExecutor Constructor

```yaml
prompt_info:
  id: "prompt-0012"
  task_type: "debug"
  source_ref: "change-0002"
  date: "2025-12-10"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0002"
    change_iteration: 1

specification:
  description: "Add PlatformConfig parameter to BinaryExecutor constructor"
  requirements:
    functional:
      - "Accept config: PlatformConfig in __init__"
      - "Store config as instance variable"
      - "Use config.sed_path, awk_path, diff_path in execute()"

design:
  components:
    - name: "BinaryExecutor.__init__"
      logic:
        - "def __init__(self, config: PlatformConfig)"
        - "self.config = config"

deliverable:
  files:
    - path: "src/sed_awk_mcp/platform/executor.py"

success_criteria:
  - "BinaryExecutor(config) instantiates successfully"
  - "TC-023, TC-024, TC-025 pass"

metadata:
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
