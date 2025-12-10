# T04 Prompt: list_allowed_directories Tool

```yaml
prompt_info:
  id: "prompt-0009"
  task_type: "code_generation"
  source_ref: "design-0003-component_tools_list"
  date: "2025-12-10"
  priority: "low"
  iteration: 1

specification:
  description: "Create list_allowed_directories MCP tool to display accessible directories"
  requirements:
    functional:
      - "Query PathValidator.list_allowed()"
      - "Format as bulleted list"
  dependencies:
    internal: ["PathValidator"]

deliverable:
  files:
    - path: "src/sed_awk_mcp/tools/list_tool.py"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
