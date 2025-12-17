Created: 2025 December 17

# Change Document: FastMCP Singleton Instance Implementation

---

## Table of Contents

1. [Change Information](#1-change-information)
2. [Source](#2-source)
3. [Scope](#3-scope)
4. [Rationale](#4-rationale)
5. [Technical Details](#5-technical-details)
6. [Dependencies](#6-dependencies)
7. [Testing Requirements](#7-testing-requirements)
8. [Implementation](#8-implementation)
9. [Verification](#9-verification)
10. [Traceability](#10-traceability)
11. [Notes](#11-notes)
12. [Version History](#12-version-history)

---

## 1. Change Information

```yaml
change_info:
  id: "change-0009"
  title: "Implement FastMCP Singleton Instance Pattern"
  date: "2025-12-17"
  author: "Claude Desktop"
  status: "proposed"
  priority: "critical"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0009"
    issue_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2. Source

```yaml
source:
  type: "issue"
  reference: "issue-0009-fastmcp-tool-registration-failure.md"
  description: "Multiple FastMCP instances prevent tool decorator registration from reaching running server instance"
```

[Return to Table of Contents](#table-of-contents)

---

## 3. Scope

```yaml
scope:
  summary: "Refactor to single shared FastMCP instance accessible across all modules"
  affected_components:
    - name: "MCP Instance Module (new)"
      file_path: "src/sed_awk_mcp/mcp_instance.py"
      change_type: "add"
    - name: "Server Main"
      file_path: "src/sed_awk_mcp/server.py"
      change_type: "modify"
    - name: "SedTools"
      file_path: "src/sed_awk_mcp/tools/sed_tool.py"
      change_type: "modify"
    - name: "AwkTool"
      file_path: "src/sed_awk_mcp/tools/awk_tool.py"
      change_type: "modify"
    - name: "DiffTool"
      file_path: "src/sed_awk_mcp/tools/diff_tool.py"
      change_type: "modify"
    - name: "ListTool"
      file_path: "src/sed_awk_mcp/tools/list_tool.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0003-component_server_main.md"
      sections:
        - "FastMCP Integration"
        - "Component Architecture"
  out_of_scope:
    - "Component injection mechanism (unchanged)"
    - "Tool function signatures (unchanged)"
    - "Security validation logic (unchanged)"
```

[Return to Table of Contents](#table-of-contents)

---

## 4. Rationale

```yaml
rational:
  problem_statement: |
    Tool decorators (@mcp.tool()) register to local FastMCP instances in each tool module.
    Server runs different instance, has no registered tools. MCP client receives empty tools list.
    
  proposed_solution: |
    Create singleton mcp_instance.py module exporting single FastMCP instance.
    All modules import from this shared instance. Tool decorators register to correct instance.
    
  alternatives_considered:
    - option: "Pass mcp instance through initialize_components()"
      reason_rejected: "Would require changing all tool initialization signatures and complicate architecture"
    - option: "Late binding after component initialization"
      reason_rejected: "Decorators execute at import time, cannot delay registration"
      
  benefits:
    - "Single source of truth for FastMCP instance"
    - "Minimal code changes required"
    - "Preserves existing component injection pattern"
    - "Standard Python singleton pattern"
    
  risks:
    - risk: "Import order dependencies"
      mitigation: "mcp_instance.py has no dependencies on other modules"
    - risk: "Module initialization timing"
      mitigation: "FastMCP instance created at import, before decorators execute"
```

[Return to Table of Contents](#table-of-contents)

---

## 5. Technical Details

```yaml
technical_details:
  current_behavior: |
    Each module creates own FastMCP instance:
    - server.py: mcp = fastmcp.FastMCP("sed-awk-mcp")
    - sed_tool.py: mcp = fastmcp.FastMCP("sed-awk-mcp")
    - awk_tool.py: mcp = fastmcp.FastMCP("sed-awk-mcp")
    - diff_tool.py: mcp = fastmcp.FastMCP("sed-awk-mcp")
    - list_tool.py: mcp = fastmcp.FastMCP("sed-awk-mcp")
    
    Tool decorators bind to local instances, server runs different instance.
    
  proposed_behavior: |
    New mcp_instance.py creates single instance:
    - mcp = fastmcp.FastMCP("sed-awk-mcp")
    
    All modules import shared instance:
    - from .mcp_instance import mcp
    
    Tool decorators bind to shared instance, server runs same instance.
    
  implementation_approach: |
    1. Create src/sed_awk_mcp/mcp_instance.py
    2. Export mcp instance from module
    3. Replace local instance creation with import in each tool module
    4. Replace local instance creation with import in server.py
    5. Verify tool decorators execute after import
    
  code_changes:
    - component: "MCP Instance Module (new)"
      file: "src/sed_awk_mcp/mcp_instance.py"
      change_summary: "Create new module with singleton FastMCP instance"
      functions_affected: []
      classes_affected: []
      
    - component: "Server Main"
      file: "src/sed_awk_mcp/server.py"
      change_summary: "Replace local instance creation with import from mcp_instance"
      functions_affected:
        - "main()"
      classes_affected: []
      
    - component: "SedTools"
      file: "src/sed_awk_mcp/tools/sed_tool.py"
      change_summary: "Replace local instance creation with import from mcp_instance"
      functions_affected:
        - "sed_substitute()"
        - "preview_sed()"
      classes_affected: []
      
    - component: "AwkTool"
      file: "src/sed_awk_mcp/tools/awk_tool.py"
      change_summary: "Replace local instance creation with import from mcp_instance"
      functions_affected:
        - "awk_transform()"
      classes_affected: []
      
    - component: "DiffTool"
      file: "src/sed_awk_mcp/tools/diff_tool.py"
      change_summary: "Replace local instance creation with import from mcp_instance"
      functions_affected:
        - "diff_files()"
      classes_affected: []
      
    - component: "ListTool"
      file: "src/sed_awk_mcp/tools/list_tool.py"
      change_summary: "Replace local instance creation with import from mcp_instance"
      functions_affected:
        - "list_allowed_directories()"
      classes_affected: []
      
  data_changes: []
  
  interface_changes:
    - interface: "Module exports"
      change_type: "contract"
      details: "mcp_instance.py exports 'mcp' as public interface"
      backward_compatible: "yes"
```

[Return to Table of Contents](#table-of-contents)

---

## 6. Dependencies

```yaml
dependencies:
  internal:
    - component: "All tool modules"
      impact: "Import statement changes only"
    - component: "Server main"
      impact: "Import statement changes only"
      
  external:
    - library: "fastmcp"
      version_change: "None - same version"
      impact: "None - API usage unchanged"
      
  required_changes: []
```

[Return to Table of Contents](#table-of-contents)

---

## 7. Testing Requirements

```yaml
testing_requirements:
  test_approach: "System test verification - TC-039 and TC-040 from test-0007"
  
  test_cases:
    - scenario: "Server startup and tool discovery"
      expected_result: "MCP client receives 5 tools in response"
      
    - scenario: "Tool execution via MCP client"
      expected_result: "sed_substitute executes successfully"
      
  regression_scope:
    - "All system tests (TC-039 through TC-050)"
    - "Integration tests remain passing"
    - "Unit tests remain passing"
    
  validation_criteria:
    - "Tool list returns 5 tools"
    - "Each tool callable via MCP protocol"
    - "Component injection still functions"
    - "Security validation still active"
```

[Return to Table of Contents](#table-of-contents)

---

## 8. Implementation

```yaml
implementation:
  effort_estimate: "1 hour"
  
  implementation_steps:
    - step: "Create mcp_instance.py with singleton pattern"
      owner: "Claude Code"
      
    - step: "Update server.py import"
      owner: "Claude Code"
      
    - step: "Update all tool module imports"
      owner: "Claude Code"
      
    - step: "Verify decorator execution order"
      owner: "Claude Code"
      
    - step: "Test server startup"
      owner: "Human"
      
  rollback_procedure: |
    Git revert to commit before change implementation.
    Server functionality non-operational in current state, rollback restores same.
    
  deployment_notes: |
    Requires:
    1. Code changes committed
    2. pip install -e . (reinstall package)
    3. Restart Claude Desktop
    4. Verify tool list via MCP client
```

[Return to Table of Contents](#table-of-contents)

---

## 9. Verification

```yaml
verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []
```

[Return to Table of Contents](#table-of-contents)

---

## 10. Traceability

```yaml
traceability:
  design_updates:
    - design_ref: "design-0003-component_server_main.md"
      sections_updated:
        - "FastMCP Integration architecture"
      update_date: ""
      
  related_changes: []
  
  related_issues:
    - issue_ref: "issue-0009"
      relationship: "resolves"
```

[Return to Table of Contents](#table-of-contents)

---

## 11. Notes

Critical fix required before any MCP functionality available. Change is minimal - single new module and import statement updates. Preserves all existing component injection and security architecture.

[Return to Table of Contents](#table-of-contents)

---

## 12. Version History

| Version | Date       | Author         | Changes                     |
|---------|------------|----------------|-----------------------------|
| 1.0     | 2025-12-17 | Claude Desktop | Initial change document     |

[Return to Table of Contents](#table-of-contents)

---

**Copyright:** Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
