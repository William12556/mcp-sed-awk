# T04 Prompt: awk_transform Tool

```yaml
prompt_info:
  id: "prompt-0007"
  task_type: "code_generation"
  source_ref: "design-0003-component_tools_awk"
  date: "2025-12-10"
  priority: "high"
  iteration: 1

specification:
  description: "Create awk_transform MCP tool for field extraction and text transformation"
  requirements:
    functional:
      - "Validate input path, awk program, optional field separator"
      - "Execute awk with optional output file"
      - "Return transformed text or success message"
  dependencies:
    internal: ["SecurityValidator", "PathValidator", "BinaryExecutor", "AuditLogger"]

deliverable:
  files:
    - path: "src/sed_awk_mcp/tools/awk_tool.py"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
