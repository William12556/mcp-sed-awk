# Prompt: Fix BinaryExecutor Calling Convention

Created: 2025-12-12

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
9. [Version History](#9-version-history)

---

## 1. Prompt Information

```yaml
prompt_info:
  id: "prompt-0001"
  task_type: "debug"
  source_ref: "change-0001"
  date: "2025-12-12"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0001"
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2. Context

**Purpose:**

Fix critical API calling convention mismatch preventing server initialization and all tool executions. Integration tests revealed that BinaryExecutor is instantiated and called incorrectly across server and tool modules.

**Integration:**

This fix enables:
- Server component to initialize BinaryExecutor correctly
- All tool modules (sed, awk, diff) to execute binaries through correct API
- Integration test suite to pass
- System to become operational

**Knowledge references:**
- workspace/knowledge/ (no relevant documents)

**Constraints:**
- Must not change BinaryExecutor interface (implementation is correct)
- Must not modify PlatformConfig (working correctly)
- Must maintain thread-safety
- Must preserve all existing functionality

[Return to Table of Contents](#table-of-contents)

---

## 3. Specification

**Description:**

Fix two categories of API misuse:

1. **Server initialization bug**: BinaryExecutor instantiated without required `config` parameter
2. **Tool execution bug**: All tools call `execute(binary_path, args, timeout=N)` but method expects `execute(args, timeout=N)` where args[0] is the binary name

**Functional requirements:**

- FR-1: Server must pass `platform_config` to BinaryExecutor constructor
- FR-2: Tools must call execute() with args list beginning with binary name
- FR-3: No changes to BinaryExecutor or PlatformConfig implementations
- FR-4: Preserve all existing error handling and logging
- FR-5: Maintain backup/rollback functionality in sed_tool

**Technical requirements:**

```yaml
requirements:
  functional:
    - "Correct server.py line 116: BinaryExecutor(platform_config)"
    - "Correct sed_tool.py execute calls: ['sed'] + normalized_args"
    - "Correct awk_tool.py execute calls: ['awk'] + normalized_args"
    - "Correct diff_tool.py execute calls: ['diff'] + normalized_args"
    - "Preserve all existing functionality"
  technical:
    language: "Python"
    version: "3.11+"
    standards:
      - "No functional changes beyond API fix"
      - "Preserve existing error handling"
      - "Maintain debug logging"
      - "No new imports required"
```

**Performance:**

No performance impact - purely correctness fix

[Return to Table of Contents](#table-of-contents)

---

## 4. Design

**Architecture:**

API calling convention fix only - no architectural changes

**Components:**

### Component 1: Server Initialization Fix

**Name:** initialize_components
**Type:** function
**Purpose:** Fix BinaryExecutor instantiation

**Current implementation (INCORRECT):**
```python
# Line 116 of server.py
binary_executor = BinaryExecutor()
```

**Required fix:**
```python
binary_executor = BinaryExecutor(platform_config)
```

**Logic:**
1. PlatformConfig already initialized at line 109
2. Pass platform_config to BinaryExecutor constructor
3. No other changes to initialize_components()

### Component 2: SedTool Execute Fix

**Name:** sed_substitute, preview_sed
**Type:** functions
**Purpose:** Fix execute() calling convention

**Current implementation (INCORRECT):**
```python
result = binary_executor.execute(
    platform_config.sed_path,
    normalized_args,
    timeout=30
)
```

**Required fix:**
```python
result = binary_executor.execute(
    ['sed'] + normalized_args,
    timeout=30
)
```

**Affected locations:**
- sed_substitute() function: ~line 166
- preview_sed() function sed call: ~line 290
- preview_sed() function diff call: ~line 312 (use ['diff'] + diff_args)

**Logic:**
1. Remove platform_config.sed_path from first argument
2. Create args list: ['sed'] + normalized_args
3. Pass timeout as named parameter only
4. BinaryExecutor.execute() internally resolves 'sed' to platform_config.sed_path

### Component 3: AwkTool Execute Fix

**Name:** awk_transform
**Type:** function
**Purpose:** Fix execute() calling convention

**Current implementation (INCORRECT):**
```python
result = binary_executor.execute(
    platform_config.awk_path,
    normalized_args,
    timeout=60
)
```

**Required fix:**
```python
result = binary_executor.execute(
    ['awk'] + normalized_args,
    timeout=60
)
```

**Affected locations:**
- awk_transform() function: ~line 160

### Component 4: DiffTool Execute Fix

**Name:** diff_files
**Type:** function
**Purpose:** Fix execute() calling convention

**Current implementation (INCORRECT):**
```python
result = binary_executor.execute(
    platform_config.diff_path,
    normalized_args,
    timeout=30
)
```

**Required fix:**
```python
result = binary_executor.execute(
    ['diff'] + normalized_args,
    timeout=30
)
```

**Affected locations:**
- diff_files() function: ~line 168

**Dependencies:**

Internal:
- BinaryExecutor (no changes)
- PlatformConfig (no changes)

External: None

[Return to Table of Contents](#table-of-contents)

---

## 5. Error Handling

**Strategy:**

No changes to error handling - preserve all existing try/except blocks and error propagation

**Exceptions:**

All existing exception handling remains unchanged

**Logging:**

All existing debug/info/error logging remains unchanged

[Return to Table of Contents](#table-of-contents)

---

## 6. Testing

**Unit tests:**

No new unit tests required - this is a fix to enable existing integration tests to pass

**Integration tests:**

Existing integration tests will verify the fix:

| Test ID | Scenario | Expected Result |
|---------|----------|-----------------|
| TC-034 | Server init with argv directories | Server initializes without TypeError |
| TC-026 | sed_substitute backup and edit | File edited successfully with backup |
| TC-029 | awk_transform field extraction | Fields extracted correctly |
| TC-030 | diff_files unified format | Unified diff generated |

**Edge cases:**

All edge cases already covered by existing integration tests

**Validation:**

Run complete integration test suite:
```bash
pytest tests/integration/ -v
```

Expected: 19/19 tests pass (currently 2/19 pass)

[Return to Table of Contents](#table-of-contents)

---

## 7. Deliverable

**Format requirements:**
- Modify existing source files in place
- No new files created
- Preserve all existing comments and docstrings

**Files to modify:**

```yaml
files:
  - path: "src/sed_awk_mcp/server.py"
    modifications:
      - line: ~116
        change: "Add platform_config parameter to BinaryExecutor()"
        
  - path: "src/sed_awk_mcp/tools/sed_tool.py"
    modifications:
      - line: ~166
        change: "Fix execute() call in sed_substitute()"
      - line: ~290
        change: "Fix execute() call in preview_sed() for sed"
      - line: ~312
        change: "Fix execute() call in preview_sed() for diff"
        
  - path: "src/sed_awk_mcp/tools/awk_tool.py"
    modifications:
      - line: ~160
        change: "Fix execute() call in awk_transform()"
        
  - path: "src/sed_awk_mcp/tools/diff_tool.py"
    modifications:
      - line: ~168
        change: "Fix execute() call in diff_files()"
```

[Return to Table of Contents](#table-of-contents)

---

## 8. Success Criteria

- Server initializes without TypeError on BinaryExecutor instantiation
- All tool execute() calls use correct API convention
- No "multiple values for argument 'timeout'" errors
- Integration test suite passes (19/19 tests)
- No regressions in existing functionality

[Return to Table of Contents](#table-of-contents)

---

## 9. Version History

| Version | Date       | Author          | Changes                                    |
|---------|------------|-----------------|--------------------------------------------|
| 1.0     | 2025-12-12 | Claude Desktop  | Initial prompt from change-0001            |

[Return to Table of Contents](#table-of-contents)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
