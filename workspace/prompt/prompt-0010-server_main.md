# T04 Prompt: FastMCP Server Main

```yaml
prompt_info:
  id: "prompt-0010"
  task_type: "code_generation"
  source_ref: "design-0004-component_server_main"
  date: "2025-12-10"
  priority: "critical"
  iteration: 1

specification:
  description: "Create FastMCP server main entry point with tool registration and configuration"
  requirements:
    functional:
      - "Parse allowed directories from sys.argv[1:] or ALLOWED_DIRECTORIES env var"
      - "Initialize all validators and components"
      - "Register all 5 tools with @mcp.tool decorator"
      - "Run FastMCP server"
    technical:
      language: "Python"
      version: "3.10+"

design:
  components:
    - name: "create_server"
      type: "function"
      logic:
        - "Parse configuration (args/env/default)"
        - "Initialize PathValidator, SecurityValidator, PlatformConfig, BinaryExecutor, AuditLogger"
        - "Create FastMCP instance"
        - "Import and register tool modules"
        - "Return mcp instance"
    - name: "main"
      type: "function"
      logic:
        - "Call create_server()"
        - "Run server"
  dependencies:
    internal: ["all components and tools"]
    external: ["fastmcp", "sys", "os"]

deliverable:
  files:
    - path: "src/sed_awk_mcp/server.py"
    - path: "src/sed_awk_mcp/__init__.py"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```
