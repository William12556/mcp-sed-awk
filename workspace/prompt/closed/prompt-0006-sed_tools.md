# T04 Prompt: sed_substitute and preview_sed Tools

```yaml
prompt_info:
  id: "prompt-0006"
  task_type: "code_generation"
  source_ref: "design-0003-component_tools_sed"
  date: "2025-12-10"
  priority: "high"
  iteration: 1

specification:
  description: "Create sed_substitute and preview_sed MCP tool functions with validation, backup, and rollback"
  
  requirements:
    functional:
      - "sed_substitute: validate inputs, create backup, execute sed, rollback on failure"
      - "preview_sed: create temp copy, apply sed, generate diff, cleanup"
      - "FastMCP @mcp.tool decorators"
      - "Line range support (optional)"
    technical:
      language: "Python"
      version: "3.10+"

design:
  components:
    - name: "sed_substitute"
      type: "async function"
      logic:
        - "Validate path (PathValidator)"
        - "Validate pattern/replacement (SecurityValidator)"
        - "Check file exists and size <10MB"
        - "Create backup if backup=True"
        - "Build sed command"
        - "Execute via BinaryExecutor"
        - "On failure: restore backup"
        - "Log via AuditLogger"
    - name: "preview_sed"
      type: "async function"
      logic:
        - "Same validation as sed_substitute"
        - "Copy file to tempfile"
        - "Apply sed to temp"
        - "Generate diff"
        - "Cleanup temp"
  dependencies:
    internal: ["SecurityValidator", "PathValidator", "BinaryExecutor", "AuditLogger"]
    external: ["fastmcp", "tempfile", "shutil"]

deliverable:
  files:
    - path: "src/sed_awk_mcp/tools/sed_tool.py"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
