Created: 2025 December 10

# Component Design: AWK Tool

## Document Information

**Document ID:** design-0003-component_tools_awk
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

**Component Name:** AWK Tool

**Purpose:** Implement awk_transform MCP tool for field extraction and transformation.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation

```python
@mcp.tool()
async def awk_transform(
    file_path: str,
    program: str,
    field_separator: Optional[str] = None,
    output_file: Optional[str] = None
) -> str:
    """Apply AWK transformation.
    
    Args:
        file_path: Input file
        program: AWK program (e.g., '{print $1}')
        field_separator: Field separator (default: whitespace)
        output_file: Optional output file
        
    Returns:
        Transformed output or confirmation if output_file specified
    """
    # Validate program
    security_validator.validate_awk_program(program)
    
    # Validate input path
    validated_input = path_validator.validate_path(file_path)
    
    # Check file size
    if validated_input.stat().st_size > MAX_FILE_SIZE:
        raise ResourceError("File exceeds size limit")
    
    # Validate output path if provided
    validated_output = None
    if output_file:
        validated_output = path_validator.validate_path(output_file)
    
    # Build AWK command
    args = []
    if field_separator:
        args.extend(['-F', field_separator])
    args.append(program)
    args.append(str(validated_input))
    
    # Normalize args
    normalized_args = platform_config.normalize_awk_args(args)
    
    # Execute
    result = binary_executor.execute(
        platform_config.awk_path,
        normalized_args
    )
    
    if not result.success:
        raise ExecutionError(f"AWK failed: {result.stderr}")
    
    # Handle output
    if validated_output:
        # Write to file
        validated_output.write_text(result.stdout)
        audit_logger.log_execution(
            "awk_transform",
            f"transform to {output_file}",
            str(validated_input)
        )
        return f"AWK output written to {output_file}"
    else:
        # Return stdout
        audit_logger.log_execution(
            "awk_transform",
            "transform",
            str(validated_input)
        )
        return result.stdout
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Testing

```python
def test_basic_transform(tmp_path):
    """Basic field extraction."""
    file = tmp_path / "data.txt"
    file.write_text("one two three\nfour five six\n")
    
    result = await awk_transform(str(file), '{print $1}')
    
    assert result == "one\nfour\n"

def test_field_separator(tmp_path):
    """Custom field separator."""
    file = tmp_path / "data.csv"
    file.write_text("a,b,c\nd,e,f\n")
    
    result = await awk_transform(
        str(file),
        '{print $2}',
        field_separator=','
    )
    
    assert result == "b\ne\n"

def test_output_file(tmp_path):
    """Write to output file."""
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.txt"
    input_file.write_text("1 2\n3 4\n")
    
    result = await awk_transform(
        str(input_file),
        '{print $1 + $2}',
        output_file=str(output_file)
    )
    
    assert "written to" in result
    assert output_file.read_text() == "3\n7\n"

def test_forbidden_function():
    """Forbidden AWK functions rejected."""
    with pytest.raises(ValidationError, match="system"):
        await awk_transform(
            "/tmp/test.txt",
            '{system("ls")}'
        )
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
