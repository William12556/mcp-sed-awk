Created: 2025 December 16

# Issue Document: Tool Registration Failure - Multiple FastMCP Instances

---

## Table of Contents

1. [Issue Information](#1-issue-information)
2. [Source](#2-source)
3. [Affected Scope](#3-affected-scope)
4. [Reproduction](#4-reproduction)
5. [Behavior](#5-behavior)
6. [Environment](#6-environment)
7. [Analysis](#7-analysis)
8. [Resolution](#8-resolution)
9. [Verification](#9-verification)
10. [Prevention](#10-prevention)
11. [Traceability](#11-traceability)
12. [Version History](#12-version-history)

---

## 1. Issue Information

```yaml
issue_info:
  id: "issue-0008"
  title: "Tool registration failure - multiple FastMCP instances"
  date: "2025-12-16"
  reporter: "Claude Desktop"
  status: "open"
  severity: "critical"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null
```

[Return to Table of Contents](#table-of-contents)

---

## 2. Source

```yaml
source:
  origin: "system_test"
  test_ref: "test-0007 (TC-039: Server Startup and Discovery)"
  description: "MCP server starts successfully but returns empty tools list when queried by Claude Desktop client"
```

**Discovery context:**
System test execution revealed that the sed-awk-mcp server initializes all components successfully, accepts MCP client connections, but returns an empty tools array when the client requests `tools/list`.

**Log evidence:**
```
2025-12-16T12:26:02.281Z [sed-awk-mcp] [info] Message from server: {"jsonrpc":"2.0","id":1,"result":{"tools":[]}}
```

[Return to Table of Contents](#table-of-contents)

---

## 3. Affected Scope

```yaml
affected_scope:
  components:
    - name: "server.py"
      file_path: "src/sed_awk_mcp/server.py"
    - name: "sed_tool.py"
      file_path: "src/sed_awk_mcp/tools/sed_tool.py"
    - name: "awk_tool.py"
      file_path: "src/sed_awk_mcp/tools/awk_tool.py"
    - name: "diff_tool.py"
      file_path: "src/sed_awk_mcp/tools/diff_tool.py"
    - name: "list_tool.py"
      file_path: "src/sed_awk_mcp/tools/list_tool.py"
  designs:
    - design_ref: "design-0003-component_server_main.md"
    - design_ref: "design-0004-component_tools_sed.md"
    - design_ref: "design-0005-component_tools_awk.md"
    - design_ref: "design-0006-component_tools_diff.md"
    - design_ref: "design-0007-component_tools_list.md"
  version: "0.1.0"
```

[Return to Table of Contents](#table-of-contents)

---

## 4. Reproduction

```yaml
reproduction:
  prerequisites: "MCP server installed, Claude Desktop configured with sed-awk-mcp server entry"
  steps:
    - "Configure Claude Desktop with sed-awk-mcp server pointing to /tmp/mcp-test"
    - "Start Claude Desktop (server auto-starts)"
    - "In Claude Desktop, request: 'List all available MCP tools'"
    - "Observe: No sed-awk-mcp tools appear in the list"
    - "Check logs: tail ~/Library/Logs/Claude/mcp-server-sed-awk-mcp.log"
    - "Observe: Server returns empty tools array: {\"tools\":[]}"
  frequency: "always"
  reproducibility_conditions: "Occurs on every server startup with current codebase"
  preconditions: "None - issue is architectural"
  test_data: "Not applicable"
  error_output: |
    Server log shows:
    2025-12-16 13:26:02,220 - __main__ - INFO - Starting sed-awk-diff MCP Server
    2025-12-16T12:26:02.281Z [sed-awk-mcp] [info] Message from server: {"jsonrpc":"2.0","id":1,"result":{"tools":[]}}
    
    Client sees no tools from sed-awk-mcp server.
```

[Return to Table of Contents](#table-of-contents)

---

## 5. Behavior

```yaml
behavior:
  expected: |
    When Claude Desktop queries the MCP server for available tools, it should receive:
    - sed_substitute
    - preview_sed
    - awk_transform
    - diff_files
    - list_allowed_directories
    
    Client should be able to call these tools and receive responses.
  actual: |
    Server returns empty tools list: {"tools":[]}
    
    No tools are registered despite:
    - All tool modules being imported
    - Tool decorators (@mcp.tool()) present on all tool functions
    - Component initialization completing successfully
    - No errors during server startup
  impact: |
    Complete system failure - server is non-functional.
    - No tools available to clients
    - Cannot perform any sed/awk/diff operations
    - System testing blocked
    - Production deployment impossible
  workaround: "None available"
```

[Return to Table of Contents](#table-of-contents)

---

## 6. Environment

```yaml
environment:
  python_version: "3.11.14"
  os: "MacOS"
  dependencies:
    - library: "fastmcp"
      version: "2.13.3"
    - library: "pytest"
      version: "9.0.2"
  domain: "domain_1"
```

[Return to Table of Contents](#table-of-contents)

---

## 7. Analysis

```yaml
analysis:
  root_cause: |
    Each tool module creates its own FastMCP instance at module level, while server.py 
    creates a separate FastMCP instance. Tool decorators register functions with their 
    module-level instance, but the server runs its own instance which has no registered tools.
    
    Evidence in code:
    
    src/sed_awk_mcp/tools/sed_tool.py line 26:
      mcp = fastmcp.FastMCP("sed-awk-mcp")
      
    src/sed_awk_mcp/server.py line 179:
      mcp = fastmcp.FastMCP("sed-awk-mcp")
      
    These are TWO DIFFERENT OBJECTS. When @mcp.tool() decorators execute in tool modules, 
    they register with the module's mcp instance. When server.py calls mcp.run(), it 
    executes a different instance with no registered tools.
    
  technical_notes: |
    FastMCP decorator pattern requirements:
    1. Decorators must reference the SAME mcp instance that calls .run()
    2. Module-level mcp instances don't share registered tools
    3. Multiple FastMCP("same-name") calls create distinct objects
    
    Current architecture violates requirement #1.
    
    The server initialization sequence:
    1. server.py imports tool modules (triggers module-level mcp creation in each)
    2. Tool decorators register with their module-level mcp instances
    3. server.py creates its own mcp instance
    4. server.py calls its mcp.run() - which has no tools
    
  related_issues: []
```

**Architectural flaw:**

The current design has each tool module owning its own `mcp` instance:

```python
# sed_tool.py
mcp = fastmcp.FastMCP("sed-awk-mcp")

@mcp.tool()
async def sed_substitute(...):
    ...
```

But `server.py` creates a different instance:

```python
# server.py
def create_server(allowed_dirs):
    initialize_components(allowed_dirs)
    mcp = fastmcp.FastMCP("sed-awk-mcp")  # Different object!
    return mcp
```

**Why this fails:**

1. When Python imports `sed_tool`, line 26 creates a FastMCP instance
2. The decorator `@mcp.tool()` registers `sed_substitute` with that instance
3. `server.py` creates its own FastMCP instance (different object)
4. `server.py` runs its instance, which has no registered tools

[Return to Table of Contents](#table-of-contents)

---

## 8. Resolution

```yaml
resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-16"
  approach: |
    Replace module-level mcp instances with a shared singleton pattern or pass the 
    server's mcp instance to tool modules during initialization.
    
    Recommended solution: Create shared mcp instance in server.py, import it in tool modules.
    
    Implementation:
    1. Create singleton mcp instance in server.py before tool imports
    2. Tool modules import the server's mcp instance instead of creating their own
    3. Ensure decorators reference the imported instance
    4. Verify all tools register with the server's instance
  change_ref: ""
  resolved_date: ""
  resolved_by: ""
  fix_description: ""
```

**Proposed solution architecture:**

```python
# server.py (before tool imports)
mcp = fastmcp.FastMCP("sed-awk-mcp")  # Create ONCE

# Then import tools (they'll use this instance)
from .tools import sed_tool, awk_tool, diff_tool, list_tool

# sed_tool.py (modified)
from ..server import mcp  # Import server's instance, don't create new one

@mcp.tool()
async def sed_substitute(...):
    ...
```

This ensures all decorators register with the same instance that runs.

[Return to Table of Contents](#table-of-contents)

---

## 9. Verification

```yaml
verification:
  verified_date: ""
  verified_by: ""
  verification_steps:
    - "Start MCP server with test directory"
    - "Query server via Claude Desktop: 'List all available MCP tools'"
    - "Verify all 5 tools appear: sed_substitute, preview_sed, awk_transform, diff_files, list_allowed_directories"
    - "Test each tool with simple operation to confirm functionality"
    - "Check server logs confirm tool registration count = 5"
  test_results: ""
  closure_notes: ""
```

[Return to Table of Contents](#table-of-contents)

---

## 10. Prevention

```yaml
prevention:
  preventive_measures: |
    - Add explicit tool registration count logging during server startup
    - Add assertion in server.py checking mcp._tools or equivalent to verify tools registered
    - Document FastMCP decorator pattern requirements in design documents
    - Add integration test verifying tool list before server.run()
  process_improvements: |
    - Design reviews should verify singleton/shared instance patterns for decorator-based frameworks
    - System test should include explicit tool discovery verification before functional testing
```

[Return to Table of Contents](#table-of-contents)

---

## 11. Traceability

```yaml
traceability:
  design_refs:
    - "design-0003-component_server_main.md"
    - "design-0004-component_tools_sed.md"
  change_refs: []
  test_refs:
    - "test-0007-system_mcp_integration.md (TC-039)"
```

[Return to Table of Contents](#table-of-contents)

---

## 12. Version History

| Version | Date       | Author          | Changes                               |
|---------|------------|-----------------|---------------------------------------|
| 1.0     | 2025-12-16 | Claude Desktop  | Initial issue creation from system test |

[Return to Table of Contents](#table-of-contents)

---

**Copyright:** Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
