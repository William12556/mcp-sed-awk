Created: 2025 December 12

# Test Document: System Testing - MCP Client Integration

---

## Table of Contents

1. [Test Information](#1-test-information)
2. [Source](#2-source)
3. [Scope](#3-scope)
4. [Test Environment](#4-test-environment)
5. [Test Cases](#5-test-cases)
6. [Coverage](#6-coverage)
7. [Test Execution Summary](#7-test-execution-summary)
8. [Defect Summary](#8-defect-summary)
9. [Verification](#9-verification)
10. [Traceability](#10-traceability)
11. [Version History](#11-version-history)

---

## 1. Test Information

```yaml
test_info:
  id: "test-0007"
  title: "System Testing - MCP Client Integration"
  date: "2025-12-12"
  author: "Claude Desktop"
  status: "planned"
  type: "system"
  priority: "critical"
  iteration: 1
  coupled_docs:
    prompt_ref: ""
    prompt_iteration: null
    result_ref: ""
```

[Return to Table of Contents](#table-of-contents)

---

## 2. Source

```yaml
source:
  test_target: "Complete MCP sed/awk/diff server deployment and client integration"
  design_refs:
    - "design-0000-master_mcp-sed-awk.md"
    - "design-0003-component_server_main.md"
  change_refs: []
  requirement_refs:
    - "FR-01: sed substitution with security validation"
    - "FR-02: awk transformation with field extraction"
    - "FR-03: diff file comparison"
    - "FR-04: preview changes without modification"
    - "FR-05: list allowed directories"
    - "FR-06: directory whitelist enforcement"
    - "FR-07: pattern security validation"
    - "FR-08: automatic backup and rollback"
    - "FR-09: GNU/BSD sed compatibility"
    - "FR-10: platform binary detection"
    - "FR-11: error recovery and reporting"
    - "FR-12: audit logging"
    - "FR-13: FastMCP integration"
    - "FR-14: MCP protocol compliance"
    - "FR-15: tool registration and discovery"
    - "NFR-01: Thread safety"
    - "NFR-02: Security (no shell injection)"
    - "NFR-03: Performance (<30s timeout)"
    - "NFR-04: File size limits (10MB)"
    - "NFR-05: Cross-platform compatibility"
```

[Return to Table of Contents](#table-of-contents)

---

## 3. Scope

```yaml
scope:
  description: "End-to-end system testing validating complete MCP server deployment, client integration, cross-platform sed/awk compatibility, and security enforcement"
  test_objectives:
    - "Verify MCP server starts and accepts client connections"
    - "Validate all five tools discoverable via MCP protocol"
    - "Confirm GNU/BSD sed/awk normalization works correctly"
    - "Verify security validation prevents malicious operations"
    - "Validate complete workflows from client request to response"
    - "Confirm error handling and audit logging operational"
  in_scope:
    - "MCP server startup and initialization"
    - "Claude Desktop client integration"
    - "All five tool operations (sed_substitute, preview_sed, awk_transform, diff_files, list_allowed_directories)"
    - "GNU vs BSD sed argument normalization"
    - "Security validation end-to-end"
    - "Error propagation to MCP client"
    - "Audit logging verification"
  out_scope:
    - "Performance benchmarking (separate test)"
    - "Stress testing with concurrent clients"
    - "Network protocol security testing"
    - "Production deployment scenarios"
  dependencies:
    - "Integration tests passing (test-0005, test-0006)"
    - "MacOS development platform with sed/awk/diff binaries"
    - "Claude Desktop with MCP client capability"
```

[Return to Table of Contents](#table-of-contents)

---

## 4. Test Environment

```yaml
test_environment:
  python_version: "3.11+"
  os: "MacOS (development platform)"
  libraries:
    - name: "fastmcp"
      version: "latest"
    - name: "pytest"
      version: "9.0.2"
  test_framework: "Manual testing with Claude Desktop MCP client"
  test_data_location: "Temporary directories created per test"
  binaries:
    sed:
      expected: "BSD sed or GNU sed"
      detection: "Automatic via PlatformConfig"
    awk:
      expected: "awk (any POSIX-compliant)"
      detection: "Automatic via PlatformConfig"
    diff:
      expected: "BSD diff or GNU diff"
      detection: "Automatic via PlatformConfig"
```

[Return to Table of Contents](#table-of-contents)

---

## 5. Test Cases

### TC-039: Server Startup and Discovery

**Category:** Positive  
**Description:** Verify MCP server starts successfully and tools are discoverable

**Preconditions:**
- Virtual environment activated
- No other MCP servers running on same port
- Project installed in development mode

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start server: `python -m sed_awk_mcp.server /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test` | Server starts without errors, logs initialization |
| 2 | Verify component initialization | Log shows: SecurityValidator, PathValidator, BinaryExecutor, AuditLogger initialized |
| 3 | Verify binary detection | Log shows sed/awk/diff paths detected |
| 4 | Check platform detection | Log shows "GNU sed detected" or "BSD sed detected" |
| 5 | Connect Claude Desktop MCP client | Client connects successfully |
| 6 | Request tool list from MCP client | Returns 5 tools: sed_substitute, preview_sed, awk_transform, diff_files, list_allowed_directories |

**Expected Outputs:**
- Server log: "Server ready - waiting for MCP client connections..."
- MCP client shows 5 available tools with descriptions

**Pass/Fail Criteria:** All tools discoverable, server accepts connections

---

### TC-040: sed_substitute End-to-End Workflow

**Category:** Positive  
**Description:** Complete sed substitution workflow via MCP client

**Preconditions:**
- Server running with `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test` as allowed directory
- Test file created: `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt` containing "hello world"

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Via MCP client, call sed_substitute("/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt", "s/world/universe/", "universe") | Operation succeeds |
| 2 | Check response message | "Successfully applied sed substitution to /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt, backup created at sample.txt.bak" |
| 3 | Verify file content | File contains "hello universe" |
| 4 | Verify backup exists | `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt.bak` contains "hello world" |
| 5 | Check audit log | Log entry shows successful sed operation |

**Expected Outputs:**
- Modified file with correct content
- Backup file preserved
- Success message returned to client
- Audit log entry created

**Pass/Fail Criteria:** File modified correctly, backup created, audit logged

---

### TC-041: Security Validation - Path Traversal Prevention

**Category:** Negative  
**Description:** Verify path traversal attempts are blocked

**Preconditions:**
- Server running with `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test` as allowed directory

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Via MCP client, attempt sed_substitute("/etc/passwd", "s/root/user/", "user") | Operation fails with SecurityError |
| 2 | Check error message | "Access denied: '/etc/passwd' not in allowed directories" |
| 3 | Verify audit log | Log shows validation failure |
| 4 | Attempt with relative path: sed_substitute("../../etc/passwd", "s/root/user/", "user") | Operation fails with SecurityError |
| 5 | Verify no file modifications | `/etc/passwd` unchanged |

**Expected Outputs:**
- SecurityError returned to client
- No file system modifications
- Audit log records attempt

**Pass/Fail Criteria:** All path traversal attempts blocked, errors logged

---

### TC-042: Security Validation - Command Injection Prevention

**Category:** Negative  
**Description:** Verify command injection attempts are blocked

**Preconditions:**
- Server running with `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test` as allowed directory
- Test file: `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt`

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Attempt sed with command injection: sed_substitute("/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt", "s/test/$(rm -rf /)/", "replacement") | ValidationError raised |
| 2 | Check error message | Error mentions forbidden pattern |
| 3 | Verify file unchanged | File content unchanged |
| 4 | Attempt sed read command: sed_substitute("/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt", "r /etc/passwd", "") | ValidationError raised |
| 5 | Attempt sed write command: sed_substitute("/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt", "w /tmp/evil", "") | ValidationError raised |

**Expected Outputs:**
- ValidationError for all malicious patterns
- No file system modifications
- Audit logs validation failures

**Pass/Fail Criteria:** All injection attempts blocked, no shell execution

---

### TC-043: GNU vs BSD sed Compatibility

**Category:** Compatibility  
**Description:** Verify sed operations work on both GNU and BSD variants

**Preconditions:**
- Server running with test directory
- Test file: `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/compat.txt` containing "line1\nline2\nline3"

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Verify detected platform | Check server log for "GNU sed" or "BSD sed" |
| 2 | Test basic substitution: sed_substitute(file, "s/line1/LINE1/", "LINE1") | Works on both platforms |
| 3 | Test in-place edit with backup | Backup created correctly on both platforms |
| 4 | Test line range: sed_substitute(file, "s/line/LINE/", "LINE", line_range="2") | Only line 2 modified on both platforms |
| 5 | Verify no platform-specific errors | No "unknown option" or "invalid flag" errors |

**Expected Outputs:**
- Operations succeed regardless of sed variant
- Correct normalization applied automatically
- Results identical on GNU vs BSD

**Pass/Fail Criteria:** All operations work correctly on both GNU and BSD sed

---

### TC-044: awk_transform Field Extraction

**Category:** Positive  
**Description:** Complete awk workflow via MCP client

**Preconditions:**
- Server running with test directory
- CSV file: `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/data.csv` containing "name,age,city\nAlice,30,NYC\nBob,25,LA"

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call awk_transform("/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/data.csv", "{print $2}", field_separator=",") | Operation succeeds |
| 2 | Check response | Contains "age\n30\n25" |
| 3 | Verify original file unchanged | CSV file unchanged |
| 4 | Check audit log | Log shows successful awk operation |

**Expected Outputs:**
- Extracted fields returned to client
- Original file preserved
- Audit log entry created

**Pass/Fail Criteria:** Fields extracted correctly, file unchanged

---

### TC-045: diff_files Comparison

**Category:** Positive  
**Description:** File comparison workflow via MCP client

**Preconditions:**
- Server running with test directory
- File1: `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/old.txt` containing "version1\ndata"
- File2: `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/new.txt` containing "version2\ndata"

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call diff_files("/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/old.txt", "/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/new.txt") | Operation succeeds |
| 2 | Check response format | Contains unified diff markers (---, +++, @@) |
| 3 | Verify diff shows changes | Shows version1 -> version2 change |
| 4 | Verify files unchanged | Both files preserved |

**Expected Outputs:**
- Unified diff returned
- Accurate change representation
- Files unchanged

**Pass/Fail Criteria:** Diff generated correctly, files preserved

---

### TC-046: preview_sed Non-Destructive Preview

**Category:** Positive  
**Description:** Preview changes without file modification

**Preconditions:**
- Server running with test directory
- Test file: `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/preview.txt` containing "test data"

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call preview_sed("/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/preview.txt", "s/test/TEST/", "TEST") | Operation succeeds |
| 2 | Check response | Contains diff showing test -> TEST |
| 3 | Verify original file unchanged | File still contains "test data" |
| 4 | Verify no backup created | No .bak file exists |

**Expected Outputs:**
- Diff preview returned
- Original file unchanged
- No backup created

**Pass/Fail Criteria:** Preview accurate, no file modifications

---

### TC-047: list_allowed_directories

**Category:** Positive  
**Description:** Directory whitelist listing

**Preconditions:**
- Server running with `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test` as allowed directory

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call list_allowed_directories() | Operation succeeds |
| 2 | Check response | Contains configured directory path |
| 3 | Verify canonical paths | Paths are absolute and resolved |

**Expected Outputs:**
- List of allowed directories
- Paths canonicalized (symlinks resolved)

**Pass/Fail Criteria:** Correct directories listed

---

### TC-048: Error Recovery - Rollback on Failure

**Category:** Error Handling  
**Description:** Verify backup restoration on operation failure

**Preconditions:**
- Server running with test directory
- Test file: `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/rollback.txt` containing "original content"

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Attempt operation with invalid pattern: sed_substitute(file, "s/test/replacement/e", "replacement") | ValidationError raised |
| 2 | Verify file unchanged | File still contains "original content" |
| 3 | Verify no backup created | No .bak file exists (operation failed before backup) |
| 4 | Check audit log | Log shows validation failure |

**Expected Outputs:**
- Error returned to client
- File unchanged
- No corrupted state

**Pass/Fail Criteria:** File protected from invalid operations

---

### TC-049: Large File Rejection

**Category:** Resource Limits  
**Description:** Verify files exceeding size limits are rejected

**Preconditions:**
- Server running with test directory
- Large file: `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/large.txt` > 10MB

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Attempt sed_substitute on large file | ResourceError raised |
| 2 | Check error message | "File size X bytes exceeds limit of 10485760 bytes" |
| 3 | Verify file unchanged | Large file unchanged |
| 4 | Check audit log | Log shows resource limit rejection |

**Expected Outputs:**
- ResourceError returned
- File unchanged
- Audit log entry

**Pass/Fail Criteria:** Large files rejected, limits enforced

---

### TC-050: Server Shutdown and Cleanup

**Category:** Lifecycle  
**Description:** Verify graceful server shutdown

**Preconditions:**
- Server running
- Active MCP client connection

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Send SIGINT (Ctrl+C) to server | Server begins shutdown |
| 2 | Check shutdown logging | Log shows "Received shutdown signal" |
| 3 | Verify audit log final entry | Shutdown logged with reason |
| 4 | Check client connection | Client disconnected gracefully |
| 5 | Verify no temp files left | Temporary files cleaned up |

**Expected Outputs:**
- Clean shutdown
- Audit log closed properly
- No resource leaks

**Pass/Fail Criteria:** Server shuts down cleanly, resources released

[Return to Table of Contents](#table-of-contents)

---

## 6. Coverage

```yaml
coverage:
  requirements_covered:
    - requirement_ref: "FR-01 to FR-15"
      test_cases:
        - "TC-039 to TC-050"
    - requirement_ref: "NFR-01 to NFR-05"
      test_cases:
        - "TC-039 to TC-050"
  code_coverage:
    target: "System test validates integration, not code coverage"
    achieved: "N/A for system testing"
  untested_areas:
    - component: "Performance under load"
      reason: "Requires separate performance test"
    - component: "Concurrent client handling"
      reason: "Out of scope for initial system test"
```

[Return to Table of Contents](#table-of-contents)

---

## 7. Test Execution Summary

```yaml
test_execution_summary:
  total_cases: 12
  passed: 0
  failed: 0
  blocked: 0
  skipped: 0
  pass_rate: ""
  execution_time: ""
  test_cycle: "Initial"
```

[Return to Table of Contents](#table-of-contents)

---

## 8. Defect Summary

```yaml
defect_summary:
  total_defects: 0
  critical: 0
  high: 0
  medium: 0
  low: 0
  issues: []
```

[Return to Table of Contents](#table-of-contents)

---

## 9. Verification

```yaml
verification:
  verified_date: ""
  verified_by: ""
  verification_notes: ""
  sign_off: ""
```

[Return to Table of Contents](#table-of-contents)

---

## 10. Traceability

```yaml
traceability:
  requirements:
    - requirement_ref: "FR-01 to FR-15, NFR-01 to NFR-05"
      test_cases:
        - "TC-039 to TC-050"
  designs:
    - design_ref: "design-0000-master_mcp-sed-awk.md"
      test_cases:
        - "TC-039 to TC-050"
    - design_ref: "design-0003-component_server_main.md"
      test_cases:
        - "TC-039, TC-050"
  changes: []
```

[Return to Table of Contents](#table-of-contents)

---

## 11. Version History

| Version | Date       | Author          | Changes                               |
|---------|------------|-----------------|---------------------------------------|
| 1.0     | 2025-12-12 | Claude Desktop  | Initial system test document creation |

[Return to Table of Contents](#table-of-contents)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
