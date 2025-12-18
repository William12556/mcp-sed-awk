Created: 2025 December 16

# Code Generation Prompt: Fix FastMCP Instance Architecture

---

## Table of Contents

1. [Prompt Information](#1-prompt-information)
2. [Context](#2-context)
3. [Specification](#3-specification)
4. [Design](#4-design)
5. [Data Schema](#5-data-schema)
6. [Error Handling](#6-error-handling)
7. [Testing](#7-testing)
8. [Deliverable](#8-deliverable)
9. [Success Criteria](#9-success-criteria)

---

## 1. Prompt Information

```yaml
prompt_info:
  id: "prompt-0008"
  task_type: "debug"
  source_ref: "change-0008-fix-fastmcp-instance-architecture.md"
  date: "2025-12-16"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0008"
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2. Context

```yaml
context:
  purpose: |
    Fix critical architectural defect preventing tool registration. Currently, each tool 
    module creates its own FastMCP instance while server.py creates a separate instance. 
    Tool decorators register with module instances, but server runs a different instance, 
    resulting in empty tools list.
    
  integration: |
    This fix enables the MCP server to properly register all 5 tools (sed_substitute, 
    preview_sed, awk_transform, diff_files, list_allowed_directories) so they are 
    discoverable and callable by MCP clients like Claude Desktop.
    
  knowledge_references: []
  
  constraints:
    - "Maintain decorator pattern - cannot change @mcp.tool() usage"
    - "No changes to tool function implementations"
    - "Preserve component initialization logic"
    - "Must avoid circular import issues"
```

[Return to Table of Contents](#table-of-contents)

---

## 3. Specification

```yaml
specification:
  description: |
    Refactor FastMCP instance creation to use singleton pattern. Create the mcp instance 
    at module level in server.py BEFORE importing tool modules. Tool modules import the 
    server's mcp instance instead of creating their own.
    
  requirements:
    functional:
      - "Single FastMCP instance shared across server and all tool modules"
      - "Tool decorators register with server's mcp instance"
      - "Server runs the instance with all registered tools"
      - "Tools discoverable via MCP protocol tools/list"
      - "Tool count verification logging at server startup"
      
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "No changes to tool function signatures or implementations"
        - "Maintain existing import structure where possible"
        - "Add assertion for tool registration count"
        
  performance:
    - target: "Server startup time unchanged"
      metric: "< 1 second"
```

[Return to Table of Contents](#table-of-contents)

---

## 4. Design

```yaml
design:
  architecture: "Singleton pattern for FastMCP instance with early initialization"
  
  components:
    - name: "server.py"
      type: "module"
      purpose: "Create singleton mcp instance and coordinate server startup"
      interface:
        inputs:
          - name: "allowed_dirs"
            type: "List[str]"
            description: "Command line or environment directory whitelist"
        outputs:
          type: "None"
          description: "Runs server until shutdown signal"
        raises:
          - "BinaryNotFoundError - required binaries not found"
          - "ValueError - configuration error"
      logic:
        - "Create mcp = fastmcp.FastMCP('sed-awk-mcp') at module level"
        - "Import tool modules AFTER mcp creation"
        - "Initialize components (existing logic)"
        - "create_server() returns module-level mcp instance"
        - "Log tool registration count"
        - "Run mcp.run()"
        
    - name: "sed_tool.py"
      type: "module"
      purpose: "Import server's mcp instance, register sed tools"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Tool registration via decorators"
        raises: []
      logic:
        - "Import mcp from ..server"
        - "Use imported mcp in @mcp.tool() decorators"
        - "No other changes to file"
        
    - name: "awk_tool.py"
      type: "module"
      purpose: "Import server's mcp instance, register awk tool"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Tool registration via decorators"
        raises: []
      logic:
        - "Import mcp from ..server"
        - "Use imported mcp in @mcp.tool() decorator"
        - "No other changes to file"
        
    - name: "diff_tool.py"
      type: "module"
      purpose: "Import server's mcp instance, register diff tool"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Tool registration via decorators"
        raises: []
      logic:
        - "Import mcp from ..server"
        - "Use imported mcp in @mcp.tool() decorator"
        - "No other changes to file"
        
    - name: "list_tool.py"
      type: "module"
      purpose: "Import server's mcp instance, register list tool"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Tool registration via decorators"
        raises: []
      logic:
        - "Import mcp from ..server"
        - "Use imported mcp in @mcp.tool() decorator"
        - "No other changes to file"
        
  dependencies:
    internal:
      - "server.py must create mcp before importing tool modules"
      - "Tool modules must import mcp from server"
    external:
      - "fastmcp>=0.1.0"
```

**Critical implementation details:**

```python
# server.py - NEW STRUCTURE
#!/usr/bin/env python3
"""sed-awk-diff MCP Server entry point."""

import logging
import os
import sys
from typing import List, Optional

import fastmcp

# Import security and platform components FIRST
from .security.validator import SecurityValidator
from .security.path_validator import PathValidator, SecurityError
from .security.audit import AuditLogger
from .platform.config import PlatformConfig, BinaryNotFoundError
from .platform.executor import BinaryExecutor

# CREATE MCP INSTANCE BEFORE TOOL IMPORTS
mcp = fastmcp.FastMCP("sed-awk-mcp")

# NOW import tool modules - decorators will register with above instance
from .tools import sed_tool, awk_tool, diff_tool, list_tool

# ... rest of server.py code ...

def create_server(allowed_dirs: List[str]) -> fastmcp.FastMCP:
    """Create and configure the FastMCP server instance."""
    initialize_components(allowed_dirs)
    
    # Return module-level mcp instance (already has tools registered)
    logger.info("FastMCP server configured with registered tools")
    return mcp  # Return module-level instance, don't create new one
```

```python
# sed_tool.py - MODIFIED IMPORTS
"""Sed tools for MCP server."""

import logging
# ... other imports ...

# REMOVE THIS LINE:
# mcp = fastmcp.FastMCP("sed-awk-mcp")

# ADD THIS LINE:
from ..server import mcp

# Rest of file unchanged - decorators already use mcp
@mcp.tool()
async def sed_substitute(...):
    ...
```

[Return to Table of Contents](#table-of-contents)

---

## 5. Data Schema

```yaml
data_schema:
  entities: []
```

No data schema changes required.

[Return to Table of Contents](#table-of-contents)

---

## 6. Error Handling

```yaml
error_handling:
  strategy: |
    Preserve existing error handling. Add verification that tools are registered.
    
  exceptions:
    - exception: "ImportError"
      condition: "Circular import if mcp created after tool imports"
      handling: "Fail fast at startup with clear error message"
      
    - exception: "AssertionError"
      condition: "Tool registration count != 5"
      handling: "Log error with details about which tools missing"
      
  logging:
    level: "INFO"
    format: "Include tool registration count in startup logs"
```

**Add tool count verification:**

```python
# In server.py main() function, after create_server()
logger.info("=" * 60)
logger.info("Starting sed-awk-diff MCP Server")
logger.info("=" * 60)
logger.info("Allowed directories: %s", allowed_dirs)
logger.info(
    "Platform: %s sed detected", 
    'GNU' if platform_config.is_gnu_sed else 'BSD'
)
logger.info("Binary paths: %s", platform_config.binaries)

# ADD THIS VERIFICATION
# Note: FastMCP may expose registered tools differently
# Check FastMCP API for proper way to count tools
# Example (adjust based on actual FastMCP API):
logger.info("Server ready - waiting for MCP client connections...")
```

[Return to Table of Contents](#table-of-contents)

---

## 7. Testing

```yaml
testing:
  unit_tests:
    - scenario: "Server module imports without errors"
      expected: "No ImportError or circular import issues"
      
    - scenario: "Tool modules import mcp from server"
      expected: "No AttributeError, mcp instance available"
      
  edge_cases:
    - "Server startup with no allowed directories (existing test)"
    - "Server startup with invalid binary paths (existing test)"
    
  validation:
    - "Start server and check logs for tool count"
    - "Query MCP server via tools/list"
    - "Verify 5 tools returned"
    - "Execute system test TC-039"
```

[Return to Table of Contents](#table-of-contents)

---

## 8. Deliverable

```yaml
deliverable:
  format_requirements:
    - "Modify existing files in place"
    - "No new files created"
    - "Maintain all existing functionality"
    
  files:
    - path: "src/sed_awk_mcp/server.py"
      content: |
        Modify to:
        1. Create mcp = fastmcp.FastMCP("sed-awk-mcp") at module level
        2. Place mcp creation AFTER security/platform imports but BEFORE tool imports
        3. Update create_server() to return module-level mcp (not create new instance)
        4. Keep all other logic unchanged
        
    - path: "src/sed_awk_mcp/tools/sed_tool.py"
      content: |
        Modify to:
        1. Remove line: mcp = fastmcp.FastMCP("sed-awk-mcp")
        2. Add import: from ..server import mcp
        3. Keep all other code unchanged (decorators already reference mcp)
        
    - path: "src/sed_awk_mcp/tools/awk_tool.py"
      content: |
        Modify to:
        1. Remove line: mcp = fastmcp.FastMCP("sed-awk-mcp")
        2. Add import: from ..server import mcp
        3. Keep all other code unchanged
        
    - path: "src/sed_awk_mcp/tools/diff_tool.py"
      content: |
        Modify to:
        1. Remove line: mcp = fastmcp.FastMCP("sed-awk-mcp")
        2. Add import: from ..server import mcp
        3. Keep all other code unchanged
        
    - path: "src/sed_awk_mcp/tools/list_tool.py"
      content: |
        Modify to:
        1. Remove line: mcp = fastmcp.FastMCP("sed-awk-mcp")
        2. Add import: from ..server import mcp
        3. Keep all other code unchanged
```

[Return to Table of Contents](#table-of-contents)

---

## 9. Success Criteria

```yaml
success_criteria:
  - "Server starts without ImportError or circular import issues"
  - "MCP client tools/list returns 5 tools"
  - "Each tool callable via MCP protocol"
  - "All existing unit tests pass (51/51)"
  - "All existing integration tests pass (19/19)"
  - "System test TC-039 passes (tool discovery)"
```

[Return to Table of Contents](#table-of-contents)

---

**Notes:**

This is a minimal architectural fix:
- 5 files modified
- ~10 lines changed total
- No functional logic changes
- Preserves all existing behavior except tool registration now works

**Critical:** The mcp instance must be created in server.py BEFORE the line `from .tools import ...`. This ensures tool module decorators register with the server's instance when they are imported.

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
