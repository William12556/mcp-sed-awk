Created: 2025 December 17

# Issue Document: FastMCP Tool Registration Failure

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
12. [Notes](#12-notes)
13. [Version History](#13-version-history)

---

## 1. Issue Information

```yaml
issue_info:
  id: "issue-0009"
  title: "FastMCP Tool Registration Failure - Multiple Instance Problem"
  date: "2025-12-17"
  reporter: "Claude Desktop"
  status: "open"
  severity: "critical"
  type: "bug"
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
  origin: "test_result"
  test_ref: "test-0007-system_mcp_integration.md"
  description: "System test TC-039 revealed server returns empty tools list despite successful component initialization"
```

[Return to Table of Contents](#table-of-contents)

---

## 3. Affected Scope

```yaml
affected_scope:
  components:
    - name: "Server Main"
      file_path: "src/sed_awk_mcp/server.py"
    - name: "SedTools"
      file_path: "src/sed_awk_mcp/tools/sed_tool.py"
    - name: "AwkTool"
      file_path: "src/sed_awk_mcp/tools/awk_tool.py"
    - name: "DiffTool"
      file_path: "src/sed_awk_mcp/tools/diff_tool.py"
    - name: "ListTool"
      file_path: "src/sed_awk_mcp/tools/list_tool.py"
  designs:
    - design_ref: "design-0003-component_server_main.md"
  version: "0.1.0"
```

[Return to Table of Contents](#table-of-contents)

---

## 4. Reproduction

```yaml
reproduction:
  prerequisites: "Server configured in Claude Desktop MCP settings with allowed directory"
  steps:
    - "Configure sed-awk-mcp in Claude Desktop config"
    - "Restart Claude Desktop"
    - "Server initializes successfully (logs show component init)"
    - "Request tool list via MCP client"
    - "Observe empty tools array returned"
  frequency: "always"
  reproducibility_conditions: "Occurs on every server startup"
  preconditions: "None - architectural issue"
  test_data: "N/A"
  error_output: |
    MCP Log Output:
    ```
    2025-12-17 08:05:24,125 - mcp.server.lowlevel.server - INFO - Processing request of type ListToolsRequest
    2025-12-17T07:05:24.128Z [sed-awk-mcp] [info] Message from server: {"jsonrpc":"2.0","id":1,"result":{"tools":[]}}
    ```
```

[Return to Table of Contents](#table-of-contents)

---

## 5. Behavior

```yaml
behavior:
  expected: "MCP client receives 5 tools (sed_substitute, preview_sed, awk_transform, diff_files, list_allowed_directories) when requesting tool list"
  actual: "MCP client receives empty tools array despite server logging successful component initialization"
  impact: "Complete failure of MCP server functionality - no tools accessible to clients, blocking all test cases"
  workaround: "None - architectural fix required"
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
    - library: "mcp"
      version: "1.22.0"
  domain: "domain_1"
```

[Return to Table of Contents](#table-of-contents)

---

## 7. Analysis

```yaml
analysis:
  root_cause: |
    Multiple independent FastMCP instances created across codebase:
    
    1. server.py (line 172): `mcp = fastmcp.FastMCP("sed-awk-mcp")`
    2. sed_tool.py (line 26): `mcp = fastmcp.FastMCP("sed-awk-mcp")`
    3. awk_tool.py (line 24): `mcp = fastmcp.FastMCP("sed-awk-mcp")`
    4. diff_tool.py (line 22): `mcp = fastmcp.FastMCP("sed-awk-mcp")`
    5. list_tool.py (line 20): `mcp = fastmcp.FastMCP("sed-awk-mcp")`
    
    Tool decorators (@mcp.tool()) register functions to their local module instance, 
    but server.py runs a different instance. The running instance has no registered tools.
    
    FastMCP architecture requires single shared instance for decorator pattern to work.
    
  technical_notes: |
    Evidence from grep analysis:
    - All 5 @mcp.tool() decorators found in tool modules
    - Each tool module creates own mcp instance
    - server.py creates separate mcp instance
    - No shared instance mechanism exists
    
    Server initialization succeeds because component injection works independently
    of FastMCP tool registration. The disconnect occurs at MCP protocol level.
    
  related_issues:
    - issue_ref: "issue-0008"
      relationship: "related - different FastMCP architectural issue"
```

[Return to Table of Contents](#table-of-contents)

---

## 8. Resolution

```yaml
resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-17"
  approach: |
    Refactor to single shared FastMCP instance:
    
    1. Create src/sed_awk_mcp/mcp_instance.py with singleton pattern
    2. Export single mcp instance from this module
    3. Update all tool modules to import shared instance
    4. Update server.py to import and run shared instance
    5. Maintain component injection architecture (unchanged)
    
    Alternative considered: Pass mcp instance through initialize_components()
    Rejected: Would require changing all tool initialization signatures
    
  change_ref: ""
  resolved_date: ""
  resolved_by: ""
  fix_description: ""
```

[Return to Table of Contents](#table-of-contents)

---

## 9. Verification

```yaml
verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""
  
verification_enhanced:
  verification_steps:
    - "Restart Claude Desktop with updated code"
    - "Request tool list via MCP client"
    - "Verify 5 tools returned in response"
    - "Execute TC-039 from test-0007"
    - "Proceed with TC-040 (sed_substitute workflow)"
  verification_results: ""
```

[Return to Table of Contents](#table-of-contents)

---

## 10. Prevention

```yaml
prevention:
  preventive_measures: |
    - Add architectural review for shared state patterns
    - Document FastMCP singleton requirement in design
    - Add integration test verifying tool count matches decorated functions
    
  process_improvements: |
    - System tests should run before claiming component completion
    - MCP tool registration should be verified in integration tests
    - Architecture patterns requiring global state need explicit design documentation
```

[Return to Table of Contents](#table-of-contents)

---

## 11. Traceability

```yaml
traceability:
  design_refs:
    - "design-0003-component_server_main.md"
  change_refs: []
  test_refs:
    - "test-0007-system_mcp_integration.md"
```

[Return to Table of Contents](#table-of-contents)

---

## 12. Notes

This is a critical architectural defect blocking all system functionality. The component injection architecture works correctly, but the FastMCP decorator pattern requires a different approach for instance management. Fix must maintain security component injection while establishing shared MCP instance.

[Return to Table of Contents](#table-of-contents)

---

## 13. Version History

| Version | Date       | Author          | Changes                    |
|---------|------------|-----------------|----------------------------|
| 1.0     | 2025-12-17 | Claude Desktop  | Initial issue creation     |

[Return to Table of Contents](#table-of-contents)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
