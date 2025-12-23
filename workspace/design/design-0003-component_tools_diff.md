Created: 2025 December 10

# Component Design: Diff Tool

## Document Information

**Document ID:** design-0003-component_tools_diff
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

**Component Name:** Diff Tool

**Purpose:** Generate unified diff between two files.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation

```python
@mcp.tool()
async def diff_files(
    file1_path: str,
    file2_path: str,
    context_lines: int = 3
) -> str:
    """Generate unified diff.
    
    Args:
        file1_path: First file
        file2_path: Second file
        context_lines: Context lines (default: 3)
        
    Returns:
        Unified diff output or empty string if identical
    """
    # Validate paths
    validated_file1 = path_validator.validate_path(file1_path)
    validated_file2 = path_validator.validate_path(file2_path)
    
    # Build diff command
    args = [
        '-u',
        f'-U{context_lines}',
        str(validated_file1),
        str(validated_file2)
    ]
    
    # Normalize args
    normalized_args = platform_config.normalize_diff_args(args)
    
    # Execute (diff returns 1 if files differ, 0 if identical)
    result = binary_executor.execute(
        platform_config.diff_path,
        normalized_args
    )
    
    # Log execution
    audit_logger.log_execution(
        "diff_files",
        "compare",
        f"{file1_path} vs {file2_path}"
    )
    
    # Return diff or empty string
    if result.returncode == 0:
        # Files identical
        return ""
    elif result.returncode == 1:
        # Files differ
        return result.stdout
    else:
        # Error
        raise ExecutionError(f"Diff failed: {result.stderr}")
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Testing

```python
def test_identical_files(tmp_path):
    """Identical files return empty string."""
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("content\n")
    file2.write_text("content\n")
    
    result = await diff_files(str(file1), str(file2))
    
    assert result == ""

def test_different_files(tmp_path):
    """Different files return diff."""
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("old\n")
    file2.write_text("new\n")
    
    result = await diff_files(str(file1), str(file2))
    
    assert "-old" in result
    assert "+new" in result

def test_context_lines(tmp_path):
    """Context lines parameter works."""
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("line1\nline2\nline3\n")
    file2.write_text("line1\nCHANGED\nline3\n")
    
    result = await diff_files(str(file1), str(file2), context_lines=1)
    
    assert result  # Should contain diff
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
