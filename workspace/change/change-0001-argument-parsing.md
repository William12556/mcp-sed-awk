# Change: Implement Standard CLI Argument Parsing

---

## change_info

- **id**: change-0001
- **title**: Implement Standard CLI Argument Parsing
- **date**: 2026-01-08
- **author**: William Watson
- **status**: implemented
- **priority**: high
- **iteration**: 1
- **coupled_docs**:
  - **issue_ref**: issue-0001
  - **issue_iteration**: 1

---

## source

- **type**: issue
- **reference**: [issue-0001-argument-parsing.md](<issue-0001-argument-parsing.md>)
- **description**: Fix argument parsing to support standard CLI flag-value syntax (`--allowed-directory /path`) while maintaining backward compatibility with positional arguments and environment variables.

---

## scope

### summary

Refactor `parse_allowed_directories()` function to properly parse `--allowed-directory` flags using argparse, supporting multiple directory specifications while maintaining backward compatibility.

### affected_components

- **name**: server.py
  - **file_path**: src/sed_awk_mcp/server.py
  - **change_type**: modify

### affected_designs

- **design_ref**: design-0004-component_server_server.md
  - **sections**:
    - Argument Parsing
    - Configuration Management

### out_of_scope

- Tool implementation changes
- Security validation logic changes
- Platform detection logic changes

---

## rational

### problem_statement

Current implementation expects positional arguments but Claude Desktop and standard CLI tools use flag-value pairs. The argument parser cannot distinguish between flag names and directory paths, causing startup failure.

### proposed_solution

Replace simple list processing with argparse-based argument parsing that:
1. Recognizes `--allowed-directory` as a flag accepting values
2. Supports multiple occurrences of the flag
3. Falls back to positional arguments for backward compatibility
4. Maintains environment variable support

### alternatives_considered

- **option**: Manual flag parsing with string manipulation
  - **reason_rejected**: Error-prone, difficult to extend, doesn't handle edge cases

- **option**: Require environment variable only
  - **reason_rejected**: Less flexible, non-standard for CLI tools

### benefits

- Standard CLI interface compatible with Claude Desktop
- README configuration examples become functional
- Extensible for future argument additions
- Maintains backward compatibility with existing deployments

### risks

- **risk**: Breaking changes for users with custom invocation scripts
  - **mitigation**: Support both flag and positional argument syntax

- **risk**: argparse adds dependency complexity
  - **mitigation**: argparse is Python standard library (no external dependency)

---

## technical_details

### current_behavior

```python
def parse_allowed_directories(args: List[str]) -> List[str]:
    if args:
        allowed_dirs = args  # Treats all args as directories
        logger.info("Using allowed directories from command line: %s", allowed_dirs)
```

### proposed_behavior

```python
def parse_allowed_directories(args: List[str]) -> List[str]:
    parser = argparse.ArgumentParser(
        description="MCP server for sed, awk, and diff operations"
    )
    parser.add_argument(
        '--allowed-directory',
        action='append',
        dest='allowed_directories',
        help='Directory to allow access to (can be specified multiple times)'
    )
    parser.add_argument(
        'directories',
        nargs='*',
        help='Directories to allow access to (positional)'
    )
    
    parsed = parser.parse_args(args)
    
    # Collect directories from both flag and positional arguments
    allowed_dirs = []
    if parsed.allowed_directories:
        allowed_dirs.extend(parsed.allowed_directories)
    if parsed.directories:
        allowed_dirs.extend(parsed.directories)
    
    # Fall back to environment variable if no arguments
    if not allowed_dirs and 'ALLOWED_DIRECTORIES' in os.environ:
        # ... existing environment variable logic
```

### implementation_approach

1. Import argparse module
2. Create ArgumentParser with description
3. Add `--allowed-directory` argument with `action='append'`
4. Add positional `directories` argument with `nargs='*'`
5. Merge both sources (flag and positional)
6. Maintain environment variable fallback
7. Update error messages to reflect new syntax

### code_changes

- **component**: server
  - **file**: src/sed_awk_mcp/server.py
  - **change_summary**: Replace manual argument processing with argparse-based parsing
  - **functions_affected**:
    - `parse_allowed_directories`
  - **classes_affected**: N/A

### data_changes

N/A

### interface_changes

- **interface**: Command-line invocation
  - **change_type**: signature
  - **details**: Add support for `--allowed-directory` flags while maintaining positional argument compatibility
  - **backward_compatible**: yes

---

## dependencies

### internal

N/A

### external

- **library**: argparse
  - **version_change**: N/A (Python standard library)
  - **impact**: None (already available)

### required_changes

N/A

---

## testing_requirements

### test_approach

- Unit tests for argument parsing with various input combinations
- Integration tests verifying server startup with different configurations
- Backward compatibility validation

### test_cases

- **scenario**: Flag syntax with single directory
  - **expected_result**: Directory parsed correctly

- **scenario**: Flag syntax with multiple directories
  - **expected_result**: All directories parsed correctly

- **scenario**: Positional arguments only
  - **expected_result**: Backward compatibility maintained

- **scenario**: Mixed flag and positional arguments
  - **expected_result**: All directories collected

- **scenario**: Environment variable fallback
  - **expected_result**: Environment variable used when no CLI args

- **scenario**: Invalid flag usage
  - **expected_result**: Clear error message with usage help

### regression_scope

- Existing positional argument invocations
- Environment variable configuration
- Error handling for missing directories
- Logging behavior

### validation_criteria

- Server starts successfully with `--allowed-directory` flags
- Positional arguments continue to work
- Environment variable fallback unchanged
- Error messages include proper usage information
- All existing tests pass

---

## implementation

### effort_estimate

2 hours (actual: 1.5 hours)

### implementation_steps

- **step**: Import argparse in server.py
  - **owner**: Claude Desktop
  - **status**: Completed

- **step**: Implement argparse-based parse_allowed_directories()
  - **owner**: Claude Desktop
  - **status**: Completed

- **step**: Update error messages with new usage patterns
  - **owner**: Claude Desktop
  - **status**: Completed

- **step**: Create unit tests for argument parsing
  - **owner**: Claude Desktop
  - **status**: Completed - 10 test cases in tests/test_argument_parsing.py

- **step**: Execute integration tests
  - **owner**: Human
  - **status**: Pending

### rollback_procedure

1. Revert server.py to previous version
2. Restart server with environment variable configuration
3. Update Claude Desktop configuration to use environment variables

### deployment_notes

- Update README with corrected configuration examples (already done)
- No data migration required
- No configuration file format changes
- Backward compatible - existing deployments continue to work

---

## verification

- **implemented_date**: 2026-01-08
- **implemented_by**: Claude Desktop
- **verification_date**: 2026-01-08
- **verified_by**: Human (unit tests)
- **test_results**: All 10 unit tests passed successfully
- **issues_found**: None 

---

## traceability

### design_updates

- **design_ref**: design-0004-component_server_server.md
  - **sections_updated**:
    - Command-line argument processing
    - Configuration management
  - **update_date**: 

### related_changes

N/A

### related_issues

- **issue_ref**: issue-0001
  - **relationship**: resolves

---

## notes

This change maintains full backward compatibility while adding standard CLI flag support. Existing deployments using positional arguments or environment variables will continue to function without modification.

---

## Version History

| Version | Date       | Author          | Changes                    |
| ------- | ---------- | --------------- | -------------------------- |
| 1.0     | 2026-01-08 | William Watson  | Initial change creation    |
| 1.1     | 2026-01-08 | William Watson  | Implementation completed, all tests passed |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
