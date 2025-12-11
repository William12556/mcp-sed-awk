# T04 Prompt: diff_files Tool

```yaml
prompt_info:
  id: "prompt-0008"
  task_type: "code_generation"
  source_ref: "design-0003-component_tools_diff"
  date: "2025-12-10"
  priority: "medium"
  iteration: 1

specification:
  description: "Create diff_files MCP tool for file comparison"
  requirements:
    functional:
      - "Validate both file paths"
      - "Execute diff with unified format (-u)"
      - "Return diff output (empty if identical)"
  dependencies:
    internal: ["PathValidator", "BinaryExecutor", "AuditLogger"]

deliverable:
  files:
    - path: "src/sed_awk_mcp/tools/diff_tool.py"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
