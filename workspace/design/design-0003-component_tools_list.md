Created: 2025 December 10

# Component Design: List Allowed Directories Tool

## Document Information

**Document ID:** design-0003-component_tools_list
**Document Type:** Component Design (Tier 3)
**Parent Domain:** [design-0003-domain_tools](<design-0003-domain_tools.md>)
**Status:** Draft
**Version:** 1.0
**Author:** William Watson
**Date:** 2025-12-10

## Table of Contents

1. [Component Information](<#1.0 component information>)
2. [Implementation](<#2.0 implementation>)
3. [Testing](<#3.0 testing>)

---

## 1.0 Component Information

**Component Name:** List Allowed Directories Tool

**Purpose:** Display directory whitelist to MCP client.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation

```python
@mcp.tool()
async def list_allowed_directories() -> str:
    """List allowed directories.
    
    Returns:
        Formatted list of allowed directory paths
    """
    allowed = path_validator.list_allowed()
    
    if not allowed:
        return "No allowed directories configured"
    
    # Format as bullet list
    lines = ["Allowed directories:"]
    for dir_path in sorted(allowed):
        lines.append(f"- {dir_path}")
    
    return "\n".join(lines)
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Testing

```python
def test_list_directories():
    """Should return formatted list."""
    # Mock path_validator
    path_validator.list_allowed.return_value = [
        '/tmp/test',
        '/home/user/project'
    ]
    
    result = await list_allowed_directories()
    
    assert "Allowed directories:" in result
    assert "- /tmp/test" in result
    assert "- /home/user/project" in result

def test_empty_list():
    """Empty whitelist returns message."""
    path_validator.list_allowed.return_value = []
    
    result = await list_allowed_directories()
    
    assert "No allowed directories" in result
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
