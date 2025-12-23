Created: 2025 December 10

# Component Design: Sed Tools

## Document Information

**Document ID:** design-0003-component_tools_sed
**Document Type:** Component Design (Tier 3)
**Parent Domain:** [design-0003-domain_tools](<design-0003-domain_tools.md>)
**Status:** Draft
**Version:** 1.0
**Author:** William Watson
**Date:** 2025-12-10

## Table of Contents

1. [Component Information](<#1.0 component information>)
2. [sed_substitute Implementation](<#2.0 sed substitute implementation>)
3. [preview_sed Implementation](<#3.0 preview sed implementation>)
4. [Testing Requirements](<#4.0 testing requirements>)

---

## 1.0 Component Information

**Component Name:** Sed Tools

**Purpose:** Implement sed_substitute and preview_sed MCP tools.

**Tools Implemented:**
- sed_substitute: In-place pattern substitution with backup/rollback
- preview_sed: Non-destructive change preview

[Return to Table of Contents](<#table of contents>)

---

## 2.0 sed_substitute Implementation

### 2.1 Function Signature

```python
@mcp.tool()
async def sed_substitute(
    file_path: str,
    pattern: str,
    replacement: str,
    line_range: Optional[str] = None
) -> str:
    """Perform in-place sed substitution with backup.
    
    Args:
        file_path: Target file path
        pattern: Sed pattern (e.g., 's/find/replace/')
        replacement: Replacement string
        line_range: Optional line range (e.g., '1,10')
        
    Returns:
        Confirmation message with operation details
        
    Raises:
        ValidationError: Invalid pattern or path
        SecurityError: Path outside whitelist
        ExecutionError: Sed execution failed
    """
```

### 2.2 Implementation Logic

```python
async def sed_substitute(
    file_path: str,
    pattern: str,
    replacement: str,
    line_range: Optional[str] = None
) -> str:
    # Step 1: Validate pattern
    security_validator.validate_sed_pattern(pattern)
    
    # Step 2: Validate path
    validated_path = path_validator.validate_path(file_path)
    
    # Step 3: Check file size
    size = validated_path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise ResourceError(f"File size {size} exceeds {MAX_FILE_SIZE} bytes")
    
    # Step 4: Create backup
    backup_path = Path(f"{validated_path}.bak")
    shutil.copy2(validated_path, backup_path)
    
    try:
        # Step 5: Build sed command
        if line_range:
            sed_pattern = f"{line_range}{pattern}"
        else:
            sed_pattern = pattern
        
        args = ['-i', sed_pattern, str(validated_path)]
        
        # Step 6: Normalize for platform
        normalized_args = platform_config.normalize_sed_args(args)
        
        # Step 7: Execute
        result = binary_executor.execute(
            platform_config.sed_path,
            normalized_args
        )
        
        # Step 8: Check result
        if not result.success:
            # Restore backup
            shutil.copy2(backup_path, validated_path)
            raise ExecutionError(f"Sed failed: {result.stderr}")
        
        # Step 9: Log success
        audit_logger.log_execution(
            "sed_substitute",
            "in-place edit",
            str(validated_path)
        )
        
        return f"Successfully applied sed substitution to {file_path}"
        
    except Exception as e:
        # Restore backup on any error
        if backup_path.exists():
            shutil.copy2(backup_path, validated_path)
        raise
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 preview_sed Implementation

### 3.1 Function Signature

```python
@mcp.tool()
async def preview_sed(
    file_path: str,
    pattern: str,
    replacement: str,
    line_range: Optional[str] = None
) -> str:
    """Preview sed operation without modification.
    
    Args:
        Same as sed_substitute
        
    Returns:
        Unified diff showing proposed changes
    """
```

### 3.2 Implementation Logic

```python
async def preview_sed(
    file_path: str,
    pattern: str,
    replacement: str,
    line_range: Optional[str] = None
) -> str:
    # Step 1-3: Same validation as sed_substitute
    security_validator.validate_sed_pattern(pattern)
    validated_path = path_validator.validate_path(file_path)
    
    # Check size
    size = validated_path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise ResourceError(f"File exceeds size limit")
    
    # Step 4: Create temp copy
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp_path = Path(tmp.name)
        shutil.copy2(validated_path, tmp_path)
    
    try:
        # Step 5: Apply sed to temp
        if line_range:
            sed_pattern = f"{line_range}{pattern}"
        else:
            sed_pattern = pattern
        
        args = ['-i', sed_pattern, str(tmp_path)]
        normalized_args = platform_config.normalize_sed_args(args)
        
        result = binary_executor.execute(
            platform_config.sed_path,
            normalized_args
        )
        
        if not result.success:
            raise ExecutionError(f"Sed preview failed: {result.stderr}")
        
        # Step 6: Generate diff
        diff_args = ['-u', str(validated_path), str(tmp_path)]
        diff_result = binary_executor.execute(
            platform_config.diff_path,
            diff_args
        )
        
        # Step 7: Return diff (empty if identical)
        return diff_result.stdout if diff_result.stdout else "No changes"
        
    finally:
        # Step 8: Always cleanup temp file
        tmp_path.unlink(missing_ok=True)
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Testing Requirements

### 4.1 sed_substitute Tests

```python
def test_basic_substitution(tmp_path):
    """Basic sed substitution should work."""
    file = tmp_path / "test.txt"
    file.write_text("hello world\n")
    
    result = await sed_substitute(
        str(file),
        's/world/universe/',
        'universe'
    )
    
    assert "Successfully applied" in result
    assert file.read_text() == "hello universe\n"
    assert (tmp_path / "test.txt.bak").exists()

def test_line_range_substitution(tmp_path):
    """Line range should be applied."""
    file = tmp_path / "test.txt"
    file.write_text("line1\nline2\nline3\n")
    
    await sed_substitute(
        str(file),
        's/line/LINE/',
        'LINE',
        line_range='1,2'
    )
    
    content = file.read_text()
    assert content == "LINE1\nLINE2\nline3\n"

def test_rollback_on_failure(tmp_path):
    """Backup should be restored on failure."""
    file = tmp_path / "test.txt"
    original = "original content\n"
    file.write_text(original)
    
    # Invalid pattern should trigger rollback
    with pytest.raises(ValidationError):
        await sed_substitute(
            str(file),
            's/a/b/e',  # Forbidden 'e' flag
            'b'
        )
    
    # Original content should be preserved
    assert file.read_text() == original

def test_file_size_limit(tmp_path):
    """Files exceeding size limit should be rejected."""
    file = tmp_path / "large.txt"
    file.write_text("x" * (MAX_FILE_SIZE + 1))
    
    with pytest.raises(ResourceError, match="exceeds"):
        await sed_substitute(str(file), 's/x/y/', 'y')

def test_path_outside_whitelist(tmp_path):
    """Paths outside whitelist should be rejected."""
    with pytest.raises(SecurityError):
        await sed_substitute('/etc/passwd', 's/root/user/', 'user')
```

### 4.2 preview_sed Tests

```python
def test_preview_no_modification(tmp_path):
    """Preview should not modify original file."""
    file = tmp_path / "test.txt"
    original = "hello world\n"
    file.write_text(original)
    
    diff = await preview_sed(str(file), 's/world/universe/', 'universe')
    
    # File should be unchanged
    assert file.read_text() == original
    
    # Diff should show change
    assert '-hello world' in diff
    assert '+hello universe' in diff

def test_preview_temp_cleanup(tmp_path):
    """Temp files should be cleaned up."""
    file = tmp_path / "test.txt"
    file.write_text("test\n")
    
    await preview_sed(str(file), 's/test/best/', 'best')
    
    # No temp files should remain
    temp_files = list(tmp_path.glob("tmp*"))
    assert len(temp_files) == 0

def test_preview_no_changes(tmp_path):
    """Preview with no matches should return 'No changes'."""
    file = tmp_path / "test.txt"
    file.write_text("hello\n")
    
    result = await preview_sed(str(file), 's/xyz/abc/', 'abc')
    
    assert result == "No changes"
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
