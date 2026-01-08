# Issue: Argument Parsing Incompatibility with Standard CLI Patterns

---

## issue_info

- **id**: issue-0001
- **title**: Argument Parsing Incompatibility with Standard CLI Patterns
- **date**: 2026-01-08
- **reporter**: William Watson
- **status**: resolved
- **severity**: high
- **type**: defect
- **iteration**: 1
- **coupled_docs**:
  - **change_ref**: change-0001
  - **change_iteration**: 1 

---

## source

- **origin**: user_report
- **test_ref**: 
- **description**: Server fails to start when Claude Desktop passes command-line arguments using standard `--flag value` syntax. The argument parser treats flag names as directory paths, causing validation failure.

---

## affected_scope

### components

- **name**: server.py
  - **file_path**: src/sed_awk_mcp/server.py

### designs

- **design_ref**: design-0004-component_server_server.md

- **version**: 1.0.0

---

## reproduction

### prerequisites

- Claude Desktop installed and configured
- MCP server installed with virtual environment
- Configuration file with `--allowed-directory` arguments

### steps

1. Configure Claude Desktop with:
   ```json
   {
     "mcpServers": {
       "sed-awk-mcp": {
         "command": "/path/to/venv/bin/mcp-sed-awk",
         "args": [
           "--allowed-directory", "/path1",
           "--allowed-directory", "/path2"
         ]
       }
     }
   }
   ```
2. Restart Claude Desktop
3. Observe server logs

### frequency

- always

### reproducibility_conditions

- Occurs whenever `--allowed-directory` flags are passed as command-line arguments
- Does not occur when using positional arguments or environment variable

### preconditions

- Server must be invoked via Claude Desktop configuration
- Arguments must use flag-value pairs

### test_data

N/A

### error_output

```
2026-01-08 08:30:16,005 - sed_awk_mcp.server - INFO - Using allowed directories from command line: ['--allowed-directory', '/Users/williamwatson/Documents/GitHub/mcp-sed-awk', '--allowed-directory', '/Users/williamwatson/Documents/GitHub/pi-netconfig']
2026-01-08 08:30:16,005 - sed_awk_mcp.server - ERROR - Configuration error: Directory does not exist: --allowed-directory
Error: Configuration error: Directory does not exist: --allowed-directory
```

---

## behavior

### expected

- Server parses `--allowed-directory` as a command-line flag
- Following arguments treated as flag values (directory paths)
- Server initializes successfully with specified allowed directories

### actual

- Server treats `--allowed-directory` strings as directory paths
- Validation fails because `--allowed-directory` is not a valid directory
- Server exits with configuration error

### impact

- Server cannot be configured via Claude Desktop using standard CLI argument patterns
- Users must use workarounds (environment variables or non-standard positional arguments)
- README configuration examples are incompatible with actual implementation

### workaround

Use environment variable configuration:
```json
{
  "mcpServers": {
    "sed-awk-mcp": {
      "command": "/path/to/venv/bin/mcp-sed-awk",
      "env": {
        "ALLOWED_DIRECTORIES": "/path1,/path2"
      }
    }
  }
}
```

---

## environment

- **python_version**: 3.11
- **os**: macOS
- **dependencies**:
  - **library**: fastmcp
    - **version**: 2.x
- **domain**: server

---

## analysis

### root_cause

The `parse_allowed_directories()` function in `server.py` treats all command-line arguments as positional directory paths without parsing flag syntax:

```python
def parse_allowed_directories(args: List[str]) -> List[str]:
    if args:
        allowed_dirs = args  # Treats entire list as directories
        logger.info("Using allowed directories from command line: %s", allowed_dirs)
```

When Claude Desktop passes `["--allowed-directory", "/path1", "--allowed-directory", "/path2"]`, the function attempts to validate `"--allowed-directory"` as a directory path.

### technical_notes

Current implementation expects either:
1. Positional arguments: `mcp-sed-awk /path1 /path2`
2. Environment variable: `ALLOWED_DIRECTORIES=/path1,/path2`

Standard CLI tools use flag-value pairs for clarity and extensibility. The server should support both patterns.

### related_issues

N/A

---

## resolution

- **assigned_to**: Claude Desktop
- **target_date**: 2026-01-08
- **approach**: Implement proper argument parsing using argparse to handle `--allowed-directory` flags with values. Maintain backward compatibility with positional arguments.
- **change_ref**: change-0001
- **resolved_date**: 2026-01-08
- **resolved_by**: Claude Desktop
- **fix_description**: Refactored `parse_allowed_directories()` function to use Python's argparse module. The function now supports flag-based syntax (`--allowed-directory /path`), positional arguments, and environment variables. Implementation maintains full backward compatibility while adding standard CLI patterns. All unit tests pass successfully. 

---

## verification

- **verified_date**: 
- **verified_by**: 
- **test_results**: 
- **closure_notes**: 

### verification_steps

1. Configure Claude Desktop with `--allowed-directory` flag syntax
2. Restart Claude Desktop
3. Verify server starts successfully
4. Verify allowed directories are correctly configured
5. Test positional argument syntax (backward compatibility)
6. Test environment variable syntax (backward compatibility)

### verification_results

---

## prevention

### preventive_measures

- Add integration test validating argument parsing with flag syntax
- Add integration test validating backward compatibility with positional arguments
- Document supported argument patterns in README

### process_improvements

- Include CLI argument parsing validation in pre-release testing
- Add example Claude Desktop configurations to integration tests

---

## traceability

### design_refs

- design-0004-component_server_server.md

### change_refs

### test_refs

---

## notes

This issue prevents the server from being configured using the standard CLI pattern documented in README.md. The current workaround using environment variables is functional but non-standard.

---

## Version History

| Version | Date       | Author          | Changes                    |
| ------- | ---------- | --------------- | -------------------------- |
| 1.0     | 2026-01-08 | William Watson  | Initial issue creation     |
| 1.1     | 2026-01-08 | William Watson  | Issue resolved, implementation completed |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
