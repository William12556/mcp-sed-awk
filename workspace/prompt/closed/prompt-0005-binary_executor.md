# T04 Prompt: BinaryExecutor Component

```yaml
prompt_info:
  id: "prompt-0005"
  task_type: "code_generation"
  source_ref: "design-0002-component_platform_executor"
  date: "2025-12-10"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

specification:
  description: "Create BinaryExecutor that safely executes sed/awk/diff with timeout, resource limits, no shell invocation"
  
  requirements:
    functional:
      - "Execute binaries via subprocess.run with shell=False"
      - "Enforce 30s timeout"
      - "Set resource limits on Linux (100MB memory, 30s CPU)"
      - "Capture stdout/stderr"
      - "Return ExecutionResult dataclass"
    technical:
      language: "Python"
      version: "3.10+"

design:
  components:
    - name: "BinaryExecutor"
      logic:
        - "execute: run subprocess with timeout, limits"
        - "_set_limits (Linux only): use resource module"
    - name: "ExecutionResult"
      type: "dataclass"
      logic:
        - "Fields: returncode, stdout, stderr, timed_out"
  dependencies:
    internal: ["PlatformConfig"]
    external: ["subprocess", "resource", "dataclasses"]

deliverable:
  files:
    - path: "src/sed_awk_mcp/platform/executor.py"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
