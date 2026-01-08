# Prompt: Implement Standard CLI Argument Parsing

---

## prompt_info

- **id**: prompt-0001
- **task_type**: debug
- **source_ref**: change-0001-argument-parsing.md
- **date**: 2026-01-08
- **priority**: high
- **iteration**: 1
- **coupled_docs**:
  - **change_ref**: change-0001
  - **change_iteration**: 1

---

## context

### purpose

Fix argument parsing in server.py to support standard CLI flag-value syntax (`--allowed-directory /path`) while maintaining backward compatibility with positional arguments and environment variables.

### integration

The server module is the entry point for the MCP server. It parses configuration, initializes domain components, and starts the FastMCP server. This change affects only the argument parsing logic without modifying component initialization or server operation.

### knowledge_references

- workspace/knowledge/ (none consulted - standard Python argparse implementation)

### constraints

- Must maintain backward compatibility with positional arguments
- Must preserve environment variable fallback behavior
- Must not modify component initialization logic
- Must provide clear error messages for invalid usage

---

## specification

### description

Refactor `parse_allowed_directories()` function in `src/sed_awk_mcp/server.py` to use argparse for proper CLI flag parsing. Support `--allowed-directory` flags with multiple occurrences while maintaining backward compatibility.

### requirements

#### functional

- Parse `--allowed-directory` flags with directory values
- Support multiple `--allowed-directory` flag occurrences
- Maintain positional argument support for backward compatibility
- Preserve environment variable fallback when no CLI arguments provided
- Validate all collected directories exist and are directories

#### technical

- **language**: Python
- **version**: 3.9+
- **standards**:
  - Thread-safe if concurrent access
  - Comprehensive error handling
  - Debug logging with traceback
  - Professional docstrings

### performance

N/A - Argument parsing occurs once at startup

---

## design

### architecture

Use Python's standard argparse module to create a parser that accepts both flag-based and positional directory arguments. Merge results from both sources before validation.

### components

- **name**: parse_allowed_directories
  - **type**: function
  - **purpose**: Parse and validate allowed directories from command-line arguments or environment
  - **interface**:
    - **inputs**:
      - **name**: args
        - **type**: List[str]
        - **description**: Command-line arguments (sys.argv[1:])
    - **outputs**:
      - **type**: List[str]
      - **description**: Validated list of allowed directory paths
    - **raises**:
      - ValueError: If no directories specified or validation fails
  - **logic**:
    1. Create ArgumentParser with description
    2. Add `--allowed-directory` argument with action='append'
    3. Add positional 'directories' argument with nargs='*'
    4. Parse arguments
    5. Collect directories from both flag and positional sources
    6. If no CLI directories, check environment variable
    7. If no directories from any source, use current directory with warning
    8. Validate all directories exist and are directories
    9. Return validated directory list

### dependencies

#### internal

None

#### external

- argparse (Python standard library)

---

## data_schema

N/A

---

## error_handling

### strategy

- Use argparse's built-in error handling for invalid flags
- Preserve existing ValueError exceptions for directory validation
- Log argument parsing details for troubleshooting

### exceptions

- **exception**: ValueError
  - **condition**: No directories specified after all sources checked
  - **handling**: Log error, print usage message to stderr, raise ValueError

- **exception**: ValueError
  - **condition**: Directory path does not exist
  - **handling**: Log error, print error message to stderr, raise ValueError

- **exception**: ValueError
  - **condition**: Path exists but is not a directory
  - **handling**: Log error, print error message to stderr, raise ValueError

### logging

- **level**: INFO
- **format**: Timestamp, module, level, message
- Log directory sources (CLI flags, positional, environment, default)
- Log parsed directory list before validation

---

## testing

### unit_tests

- **scenario**: Parse single `--allowed-directory` flag
  - **expected**: Single directory in returned list

- **scenario**: Parse multiple `--allowed-directory` flags
  - **expected**: All directories in returned list

- **scenario**: Parse positional arguments only
  - **expected**: All positional directories in returned list

- **scenario**: Parse mixed flags and positional arguments
  - **expected**: All directories from both sources in returned list

- **scenario**: No CLI arguments, environment variable set
  - **expected**: Environment variable directories parsed

- **scenario**: No CLI arguments, no environment variable
  - **expected**: Current working directory with warning

### edge_cases

- Empty argument list
- Invalid flag combinations
- Non-existent directory paths
- File paths instead of directories
- Relative vs absolute paths

### validation

- argparse handles invalid flag syntax
- Existing validation logic catches invalid directory paths
- Logging provides troubleshooting information

---

## deliverable

### format_requirements

- Save generated code directly to specified paths
- Maintain existing code structure and imports
- Preserve existing function signatures for other functions
- Add argparse import at module level

### files

- **path**: src/sed_awk_mcp/server.py
  - **content**: Modified parse_allowed_directories() function with argparse implementation

---

## success_criteria

- Server starts successfully with `--allowed-directory` flags
- Server starts successfully with positional arguments (backward compatibility)
- Server falls back to environment variable when no CLI args
- Server falls back to current directory when no configuration provided
- All directory validation logic preserved
- Logging provides clear troubleshooting information
- Error messages include proper usage help

---

## notes

This implementation uses Python's standard argparse library, which provides robust argument parsing with built-in help generation and error handling. The change is isolated to the `parse_allowed_directories()` function and does not affect component initialization or server operation.

---

## metadata

- **copyright**: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
- **template_version**: 1.0
- **schema_type**: t04_prompt

---

## Version History

| Version | Date       | Author          | Changes                    |
| ------- | ---------- | --------------- | -------------------------- |
| 1.0     | 2026-01-08 | William Watson  | Initial prompt creation    |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
