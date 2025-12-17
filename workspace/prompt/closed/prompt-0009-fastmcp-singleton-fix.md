Created: 2025 December 17

# Debug Prompt: FastMCP Singleton Instance Implementation

---

## Table of Contents

1. [Prompt Information](#1-prompt-information)
2. [Context](#2-context)
3. [Specification](#3-specification)
4. [Design](#4-design)
5. [Error Handling](#5-error-handling)
6. [Testing](#6-testing)
7. [Deliverable](#7-deliverable)
8. [Success Criteria](#8-success-criteria)
9. [Notes](#9-notes)
10. [Version History](#10-version-history)

---

## 1. Prompt Information

```yaml
prompt_info:
  id: "prompt-0009"
  task_type: "debug"
  source_ref: "change-0009-fastmcp-singleton-instance.md"
  date: "2025-12-17"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0009"
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2. Context

```yaml
context:
  purpose: "Fix critical bug where MCP tools not registered due to multiple FastMCP instances"
  
  integration: |
    Current architecture creates separate FastMCP instance in each module.
    Tool decorators register to local instances, server runs different instance.
    Result: MCP client receives empty tools list.
    
    Fix creates singleton instance all modules share.
    
  knowledge_references: []
  
  constraints:
    - "Preserve existing component injection architecture"
    - "Maintain all tool function signatures"
    - "Keep security validation unchanged"
    - "Minimal code disruption"
```

[Return to Table of Contents](#table-of-contents)

---

## 3. Specification

```yaml
specification:
  description: "Create shared FastMCP instance module and update all modules to use singleton"
  
  requirements:
    functional:
      - "Single FastMCP instance accessible across all modules"
      - "Tool decorators register to shared instance"
      - "Server runs same instance that has registered tools"
      - "All 5 tools appear in MCP client tool list"
      
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Module-level singleton pattern"
        - "Import at module top"
        - "No circular dependencies"
        - "Thread-safe (FastMCP handles)"
        
  performance:
    - target: "Instant tool registration at import"
      metric: "Decorator execution time"
```

[Return to Table of Contents](#table-of-contents)

---

## 4. Design

```yaml
design:
  architecture: "Singleton module pattern with shared FastMCP instance"
  
  components:
    - name: "mcp_instance"
      type: "module"
      purpose: "Provide singleton FastMCP instance"
      interface:
        inputs: []
        outputs:
          type: "fastmcp.FastMCP"
          description: "Shared MCP server instance"
        raises: []
      logic:
        - "Import fastmcp"
        - "Create single FastMCP instance"
        - "Export as module-level variable"
        
    - name: "server.py update"
      type: "modification"
      purpose: "Use shared instance instead of creating local"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Import change only"
        raises: []
      logic:
        - "Remove: mcp = fastmcp.FastMCP('sed-awk-mcp')"
        - "Add: from .mcp_instance import mcp"
        - "Keep all other code unchanged"
        
    - name: "sed_tool.py update"
      type: "modification"
      purpose: "Use shared instance"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Import change only"
        raises: []
      logic:
        - "Remove: mcp = fastmcp.FastMCP('sed-awk-mcp')"
        - "Add: from ..mcp_instance import mcp"
        
    - name: "awk_tool.py update"
      type: "modification"
      purpose: "Use shared instance"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Import change only"
        raises: []
      logic:
        - "Remove: mcp = fastmcp.FastMCP('sed-awk-mcp')"
        - "Add: from ..mcp_instance import mcp"
        
    - name: "diff_tool.py update"
      type: "modification"
      purpose: "Use shared instance"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Import change only"
        raises: []
      logic:
        - "Remove: mcp = fastmcp.FastMCP('sed-awk-mcp')"
        - "Add: from ..mcp_instance import mcp"
        
    - name: "list_tool.py update"
      type: "modification"
      purpose: "Use shared instance"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Import change only"
        raises: []
      logic:
        - "Remove: mcp = fastmcp.FastMCP('sed-awk-mcp')"
        - "Add: from ..mcp_instance import mcp"
        
  dependencies:
    internal:
      - "No new internal dependencies"
    external:
      - "fastmcp (existing)"
```

[Return to Table of Contents](#table-of-contents)

---

## 5. Error Handling

```yaml
error_handling:
  strategy: "FastMCP handles all runtime errors, no changes needed"
  
  exceptions: []
  
  logging:
    level: "INFO"
    format: "Existing logging unchanged"
```

[Return to Table of Contents](#table-of-contents)

---

## 6. Testing

```yaml
testing:
  unit_tests:
    - scenario: "Import mcp_instance module"
      expected: "Returns FastMCP instance"
      
    - scenario: "Multiple imports of mcp_instance"
      expected: "Same instance returned (singleton verified)"
      
  edge_cases:
    - "Import order - mcp_instance imported before tool modules"
    - "Circular import detection - none expected"
    
  validation:
    - "Tool list via MCP protocol returns 5 tools"
    - "sed_substitute executable via MCP"
    - "Component injection still works"
```

[Return to Table of Contents](#table-of-contents)

---

## 7. Deliverable

```yaml
deliverable:
  format_requirements:
    - "Save files directly to paths specified"
    - "Preserve all existing formatting"
    - "Maintain copyright headers"
    
  files:
    - path: "src/sed_awk_mcp/mcp_instance.py"
      content: |
        New module containing:
        - FastMCP import
        - Instance creation
        - Module docstring
        - Copyright
        
    - path: "src/sed_awk_mcp/server.py"
      content: |
        Modified:
        - Line ~18: Replace "import fastmcp" with "from .mcp_instance import mcp"
        - Line ~172: Remove "mcp = fastmcp.FastMCP('sed-awk-mcp')"
        - Everything else unchanged
        
    - path: "src/sed_awk_mcp/tools/sed_tool.py"
      content: |
        Modified:
        - Line ~26: Replace "mcp = fastmcp.FastMCP('sed-awk-mcp')" 
          with "from ..mcp_instance import mcp"
        - Remove now-unused "import fastmcp" if present
        - Everything else unchanged
        
    - path: "src/sed_awk_mcp/tools/awk_tool.py"
      content: |
        Modified:
        - Line ~24: Replace "mcp = fastmcp.FastMCP('sed-awk-mcp')"
          with "from ..mcp_instance import mcp"
        - Remove now-unused "import fastmcp" if present
        - Everything else unchanged
        
    - path: "src/sed_awk_mcp/tools/diff_tool.py"
      content: |
        Modified:
        - Line ~22: Replace "mcp = fastmcp.FastMCP('sed-awk-mcp')"
          with "from ..mcp_instance import mcp"
        - Remove now-unused "import fastmcp" if present
        - Everything else unchanged
        
    - path: "src/sed_awk_mcp/tools/list_tool.py"
      content: |
        Modified:
        - Line ~20: Replace "mcp = fastmcp.FastMCP('sed-awk-mcp')"
          with "from ..mcp_instance import mcp"
        - Remove now-unused "import fastmcp" if present
        - Everything else unchanged
```

[Return to Table of Contents](#table-of-contents)

---

## 8. Success Criteria

```yaml
success_criteria:
  - "New mcp_instance.py module created"
  - "All 6 files modified with correct imports"
  - "No syntax errors"
  - "Package installs successfully"
  - "Server starts without errors"
  - "MCP tool list returns 5 tools"
```

[Return to Table of Contents](#table-of-contents)

---

## 9. Notes

**Critical Fix:** This resolves complete failure of MCP functionality.

**Implementation Details:**
- Create mcp_instance.py FIRST before modifying other files
- Import path in server.py is relative: `from .mcp_instance import mcp`
- Import path in tool modules is parent-relative: `from ..mcp_instance import mcp`
- FastMCP instance name must remain "sed-awk-mcp"
- Preserve all existing imports except fastmcp where replaced
- Do NOT modify component injection calls (initialize_components)
- Do NOT modify tool function signatures or decorators

**Verification After Implementation:**
```bash
cd /Users/williamwatson/Documents/GitHub/mcp-sed-awk
pip install -e .
# Restart Claude Desktop
# Test tool list via MCP client
```

[Return to Table of Contents](#table-of-contents)

---

## 10. Version History

| Version | Date       | Author         | Changes                      |
|---------|------------|----------------|------------------------------|
| 1.0     | 2025-12-17 | Claude Desktop | Initial debug prompt         |

[Return to Table of Contents](#table-of-contents)

---

**Copyright:** Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
