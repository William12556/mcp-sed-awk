Created: 2025 December 16

# Change Document: Fix FastMCP Instance Architecture for Tool Registration

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
11. [Version History](#11-version-history)

---

## 1. Change Information

```yaml
change_info:
  id: "change-0008"
  title: "Fix FastMCP instance architecture for tool registration"
  date: "2025-12-16"
  author: "Claude Desktop"
  status: "proposed"
  priority: "critical"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0008"
    issue_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2. Source

```yaml
source:
  type: "issue"
  reference: "issue-0008-fastmcp-instance-mismatch.md"
  description: |
    Tool decorators register with module-level FastMCP instances, but server 
    creates and runs a different FastMCP instance, resulting in empty tools list.
```

[Return to Table of Contents](#table-of-contents)

---

## 3. Scope

```yaml
scope:
  summary: "Refactor FastMCP instance creation to use singleton pattern ensuring all tool decorators register with the server's mcp instance"
  affected_components:
    - name: "server.py"
      file_path: "src/sed_awk_mcp/server.py"
      change_type: "modify"
    - name: "sed_tool.py"
      file_path: "src/sed_awk_mcp/tools/sed_tool.py"
      change_type: "modify"
    - name: "awk_tool.py"
      file_path: "src/sed_awk_mcp/tools/awk_tool.py"
      change_type: "modify"
    - name: "diff_tool.py"
      file_path: "src/sed_awk_mcp/tools/diff_tool.py"
      change_type: "modify"
    - name: "list_tool.py"
      file_path: "src/sed_awk_mcp/tools/list_tool.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0003-component_server_main.md"
      sections:
        - "Component design"
        - "Processing logic"
  out_of_scope:
    - "Component initialization logic (no changes)"
    - "Tool function implementations (no changes)"
    - "Security validation (no changes)"
```

[Return to Table of Contents](#table-of-contents)

---

## 4. Rationale

```yaml
rational:
  problem_statement: |
    Current architecture creates multiple FastMCP instances:
    1. Each tool module creates its own: mcp = fastmcp.FastMCP("sed-awk-mcp")
    2. Server creates its own: mcp = fastmcp.FastMCP("sed-awk-mcp")
    3. Tool decorators register with module instances
    4. Server runs its instance (which has no tools)
    Result: Empty tools list returned to clients, complete system failure.
    
  proposed_solution: |
    Create singleton FastMCP instance in server.py BEFORE importing tool modules.
    Tool modules import the server's mcp instance instead of creating their own.
    All decorators reference the shared instance, ensuring tools register correctly.
    
    Architecture flow:
    1. server.py creates mcp = fastmcp.FastMCP("sed-awk-mcp")
    2. server.py imports tool modules
    3. Tool modules import mcp from server
    4. Decorators register with server's mcp instance
    5. server.py runs the same instance (now with registered tools)
    
  alternatives_considered:
    - option: "Pass mcp instance to tool modules during initialize_components()"
      reason_rejected: "Breaks decorator pattern - decorators execute at import time, before initialize_components() is called"
    - option: "Use dependency injection for mcp instance"
      reason_rejected: "Python decorators execute at module import time, too late for runtime injection"
    - option: "Create factory function for tool registration"
      reason_rejected: "Requires rewriting all tool modules to not use decorators, major architectural change"
      
  benefits:
    - "Single source of truth for FastMCP instance"
    - "Tools properly registered and discoverable"
    - "Minimal code changes (import statement modifications)"
    - "Maintains decorator pattern"
    - "No impact on tool function implementations"
    
  risks:
    - risk: "Circular import between server.py and tool modules"
      mitigation: "Create mcp instance early in server.py before any imports requiring it"
    - risk: "Module initialization order dependency"
      mitigation: "Document import order requirements, add assertions"
```

[Return to Table of Contents](#table-of-contents)

---

## 5. Technical Details

```yaml
technical_details:
  current_behavior: |
    server.py (lines 22-26):
      from .tools import sed_tool, awk_tool, diff_tool, list_tool
      
    server.py (line 179):
      mcp = fastmcp.FastMCP("sed-awk-mcp")  # Creates new instance
      
    sed_tool.py (line 26):
      mcp = fastmcp.FastMCP("sed-awk-mcp")  # Creates separate instance
      
    All other tool modules follow same pattern.
    Result: Decorators register with module instances, server runs different instance.
    
  proposed_behavior: |
    server.py (before tool imports):
      mcp = fastmcp.FastMCP("sed-awk-mcp")  # Create singleton instance
      
    server.py (after mcp creation):
      from .tools import sed_tool, awk_tool, diff_tool, list_tool
      
    sed_tool.py (modified):
      from ..server import mcp  # Import server's instance
      
    All tool modules import server's mcp, decorators register with shared instance.
    Result: Server runs instance with all registered tools.
    
  implementation_approach: |
    Phase 1: Refactor server.py
      - Move mcp instance creation to module level (before imports)
      - Remove mcp creation from create_server() function
      - Update create_server() to return the module-level mcp instance
      
    Phase 2: Refactor tool modules
      - Replace module-level mcp creation with import from server
      - Update each: sed_tool.py, awk_tool.py, diff_tool.py, list_tool.py
      - No changes to decorator usage or function implementations
      
    Phase 3: Add verification
      - Add assertion in server startup logging tool registration count
      - Document expected tool count (5 tools)
      
  code_changes:
    - component: "server.py"
      file: "src/sed_awk_mcp/server.py"
      change_summary: "Move mcp instance creation to module level before tool imports"
      functions_affected:
        - "create_server"
      classes_affected: []
      
    - component: "sed_tool.py"
      file: "src/sed_awk_mcp/tools/sed_tool.py"
      change_summary: "Replace local mcp creation with import from server"
      functions_affected: []
      classes_affected: []
      
    - component: "awk_tool.py"
      file: "src/sed_awk_mcp/tools/awk_tool.py"
      change_summary: "Replace local mcp creation with import from server"
      functions_affected: []
      classes_affected: []
      
    - component: "diff_tool.py"
      file: "src/sed_awk_mcp/tools/diff_tool.py"
      change_summary: "Replace local mcp creation with import from server"
      functions_affected: []
      classes_affected: []
      
    - component: "list_tool.py"
      file: "src/sed_awk_mcp/tools/list_tool.py"
      change_summary: "Replace local mcp creation with import from server"
      functions_affected: []
      classes_affected: []
      
  data_changes: []
  
  interface_changes:
    - interface: "create_server()"
      change_type: "behavior"
      details: "Returns module-level mcp instance instead of creating new one"
      backward_compatible: "yes"
```

[Return to Table of Contents](#table-of-contents)

---

## 6. Dependencies

```yaml
dependencies:
  internal:
    - component: "All tool modules"
      impact: "Must import mcp from server instead of creating own instance"
      
  external: []
  
  required_changes: []
```

[Return to Table of Contents](#table-of-contents)

---

## 7. Testing Requirements

```yaml
testing_requirements:
  test_approach: |
    1. Verify tool registration count at server startup
    2. Test tool discovery via MCP client (Claude Desktop)
    3. Execute system test TC-039 (Server Startup and Discovery)
    4. Verify all 5 tools appear in tools list
    5. Execute functional test for each tool
    
  test_cases:
    - scenario: "Server startup with tool registration verification"
      expected_result: "Server logs show 5 tools registered, tools/list returns 5 tools"
      
    - scenario: "MCP client tool discovery"
      expected_result: "Claude Desktop shows all 5 sed-awk-mcp tools"
      
    - scenario: "Tool execution via MCP client"
      expected_result: "Each tool executes successfully when called from Claude Desktop"
      
  regression_scope:
    - "All unit tests (51 tests)"
    - "All integration tests (19 tests)"
    - "System test TC-039 through TC-050"
    
  validation_criteria:
    - "Server startup logs show: 'Registered 5 tools'"
    - "MCP tools/list response contains exactly 5 tools"
    - "Each tool callable and functional via MCP client"
    - "All existing tests pass without modification"
```

[Return to Table of Contents](#table-of-contents)

---

## 8. Implementation

```yaml
implementation:
  effort_estimate: "1 hour"
  implementation_steps:
    - step: "Modify server.py: Move mcp creation to module level before tool imports"
      owner: "Claude Code"
    - step: "Modify sed_tool.py: Replace mcp creation with import from server"
      owner: "Claude Code"
    - step: "Modify awk_tool.py: Replace mcp creation with import from server"
      owner: "Claude Code"
    - step: "Modify diff_tool.py: Replace mcp creation with import from server"
      owner: "Claude Code"
    - step: "Modify list_tool.py: Replace mcp creation with import from server"
      owner: "Claude Code"
    - step: "Add tool count verification in server startup logging"
      owner: "Claude Code"
    - step: "Test server startup and verify tools registered"
      owner: "Human"
      
  rollback_procedure: |
    Git revert to commit before change-0008 implementation.
    Previous architecture (broken) restored.
    
  deployment_notes: |
    No deployment changes required.
    Change affects only internal module architecture.
    No configuration changes needed.
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
        - "Processing logic - FastMCP instance creation timing"
      update_date: ""
      
  related_changes: []
  
  related_issues:
    - issue_ref: "issue-0008"
      relationship: "resolves"
```

[Return to Table of Contents](#table-of-contents)

---

## 11. Version History

| Version | Date       | Author          | Changes                               |
|---------|------------|-----------------|---------------------------------------|
| 1.0     | 2025-12-16 | Claude Desktop  | Initial change document from issue-0008 |

[Return to Table of Contents](#table-of-contents)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
