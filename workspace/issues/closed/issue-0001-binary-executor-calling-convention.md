# Issue: BinaryExecutor Calling Convention Mismatch

Created: 2025-12-12

---

## Table of Contents

1. [Issue Information](#1-issue-information)
2. [Source](#2-source)
3. [Affected Scope](#3-affected-scope)
4. [Reproduction](#4-reproduction)
5. [Behavior](#5-behavior)
6. [Environment](#6-environment)
7. [Analysis](#7-analysis)
8. [Resolution](#8-resolution)
9. [Verification](#9-verification)
10. [Prevention](#10-prevention)
11. [Traceability](#11-traceability)
12. [Version History](#12-version-history)

---

## 1. Issue Information

```yaml
issue_info:
  id: "issue-0001"
  title: "BinaryExecutor calling convention mismatch"
  date: "2025-12-12"
  reporter: "Claude Desktop"
  status: "resolved"
  severity: "critical"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-0001"
    change_iteration: 1
```

[Return to Table of Contents](#table-of-contents)

---

## 2. Source

```yaml
source:
  origin: "test_result"
  test_ref: "test-0005-tools_integration.md, test-0006-server_integration.md"
  description: "Integration tests revealed incorrect calling convention for BinaryExecutor.execute() method"
```

**Details:**

Integration test execution revealed two critical defects in component initialization and tool implementation:

1. **Server initialization failure**: `BinaryExecutor()` instantiated without required `config` parameter (line 116 of server.py)
2. **Tool execution failure**: All tool modules call `binary_executor.execute(binary_path, args, timeout=timeout)` but method signature expects `execute(args, timeout=timeout)` where args[0] contains the binary name

[Return to Table of Contents](#table-of-contents)

---

## 3. Affected Scope

```yaml
affected_scope:
  components:
    - name: "Server"
      file_path: "src/sed_awk_mcp/server.py"
    - name: "SedTool"
      file_path: "src/sed_awk_mcp/tools/sed_tool.py"
    - name: "AwkTool"
      file_path: "src/sed_awk_mcp/tools/awk_tool.py"
    - name: "DiffTool"
      file_path: "src/sed_awk_mcp/tools/diff_tool.py"
  designs:
    - design_ref: "design-0003-component_server_main.md"
    - design_ref: "design-0001-component_tools_sed.md"
    - design_ref: "design-0002-component_tools_awk.md"
    - design_ref: "design-0004-component_tools_diff.md"
  version: "0.1.0"
```

[Return to Table of Contents](#table-of-contents)

---

## 4. Reproduction

**Prerequisites:**
- Python virtual environment activated
- Project installed in development mode
- Integration tests created

**Steps to reproduce:**

```bash
cd /Users/williamwatson/Documents/GitHub/mcp-sed-awk
pytest tests/integration/test_server_integration.py::test_server_init_with_argv_directories -v
```

**Frequency:** always

**Reproducibility conditions:** Occurs on every server initialization attempt and every tool execution attempt

**Error output:**

```
TypeError: BinaryExecutor.__init__() missing 1 required positional argument: 'config'
```

And for tool calls:

```
TypeError: BinaryExecutor.execute() got multiple values for argument 'timeout'
```

[Return to Table of Contents](#table-of-contents)

---

## 5. Behavior

**Expected behavior:**

1. Server initializes BinaryExecutor with platform_config: `BinaryExecutor(platform_config)`
2. Tools call execute with args list containing binary name: `execute(['sed'] + normalized_args, timeout=30)`

**Actual behavior:**

1. Server calls `BinaryExecutor()` without config parameter, causing TypeError
2. Tools call `execute(platform_config.sed_path, normalized_args, timeout=30)` passing binary_path separately, causing timeout parameter conflict

**Impact:**

- Complete failure of server initialization
- All integration tests fail (17/19 failures)
- Server cannot start
- No tool functionality available

**Workaround:** None - this is a fundamental API mismatch

[Return to Table of Contents](#table-of-contents)

---

## 6. Environment

```yaml
environment:
  python_version: "3.11.14"
  os: "Darwin (MacOS)"
  dependencies:
    - library: "pytest"
      version: "9.0.2"
    - library: "fastmcp"
      version: "latest"
  domain: "domain_1"
```

[Return to Table of Contents](#table-of-contents)

---

## 7. Analysis

**Root cause:**

Design-to-implementation disconnect in BinaryExecutor interface:

1. **BinaryExecutor.__init__() signature:**
   - Design specified: `def __init__(self, config: PlatformConfig)`
   - Implementation: Correct
   - Server.py call: **INCORRECT** - missing config parameter

2. **BinaryExecutor.execute() signature:**
   - Implementation: `def execute(self, args: List[str], timeout: int = DEFAULT_TIMEOUT, apply_limits: bool = True)`
   - Method expects: `args[0]` to be binary name ('sed', 'awk', 'diff')
   - Method internally: Resolves binary name from args[0] to full path
   - Tool calls: **INCORRECT** - pass binary_path as first arg, then normalized_args, then timeout
   
**Technical notes:**

The BinaryExecutor.execute() method design (lines 138-163 of executor.py) shows:

```python
def execute(self, args: List[str], timeout: int = DEFAULT_TIMEOUT, ...):
    binary_name = args[0]  # Extract binary name from args
    if binary_name == 'sed':
        binary_path = self.config.sed_path
    # ... resolve to full path
    cmd = [binary_path] + args[1:]  # Build command with full path + remaining args
```

But tools call it as:

```python
result = binary_executor.execute(
    platform_config.sed_path,  # WRONG: passes full path
    normalized_args,            # WRONG: these should be args[1:]
    timeout=30                  # WRONG: timeout conflicts with positional arg
)
```

**Related issues:** None

[Return to Table of Contents](#table-of-contents)

---

## 8. Resolution

```yaml
resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-12"
  approach: "Fix both initialization and calling convention issues"
  change_ref: "change-0001"
  resolved_date: "2025-12-12"
  resolved_by: "Claude Code"
  fix_description: "Fixed server.py line 116 to pass platform_config to BinaryExecutor(). Fixed all tool execute() calls to use correct convention: ['binary_name'] + args instead of (binary_path, args, timeout)."
```

**Resolution approach:**

1. Fix server.py line 116: `binary_executor = BinaryExecutor(platform_config)`
2. Fix all tool calls to use correct calling convention:
   - sed_tool.py: Replace `execute(platform_config.sed_path, normalized_args, timeout=N)` with `execute(['sed'] + normalized_args, timeout=N)`
   - awk_tool.py: Replace `execute(platform_config.awk_path, normalized_args, timeout=N)` with `execute(['awk'] + normalized_args, timeout=N)`
   - diff_tool.py: Replace `execute(platform_config.diff_path, normalized_args, timeout=N)` with `execute(['diff'] + normalized_args, timeout=N)`

[Return to Table of Contents](#table-of-contents)

---

## 9. Verification

```yaml
verification:
  verified_date: "2025-12-12"
  verified_by: "Claude Desktop"
  test_results: "Integration test suite: 19/19 tests passed (100%). All server initialization and tool execution tests passing."
  closure_notes: "Fix verified through complete integration test suite execution. Server initializes correctly, all tools execute binaries with proper API calling convention."
```

**Verification steps:**
1. Run integration test suite: `pytest tests/integration/ -v`
2. Verify server initialization succeeds
3. Verify all tool execution tests pass
4. Verify no timeout parameter conflicts

**Verification results:** Pending implementation

[Return to Table of Contents](#table-of-contents)

---

## 10. Prevention

**Preventive measures:**

1. Add interface contract tests that verify calling conventions
2. Document BinaryExecutor API contract explicitly in component design
3. Create integration tests earlier in development cycle

**Process improvements:**

1. Configuration audit should verify not just code structure but also API contract compliance
2. Add API signature verification to audit checklist
3. Ensure T04 prompts include explicit API calling examples

[Return to Table of Contents](#table-of-contents)

---

## 11. Traceability

```yaml
traceability:
  design_refs:
    - "design-0003-component_server_main.md"
    - "design-0001-component_tools_sed.md"
    - "design-0002-component_tools_awk.md"
    - "design-0004-component_tools_diff.md"
    - "design-0007-component_platform_executor.md"
  change_refs:
    - "change-0001"
  test_refs:
    - "test-0005-tools_integration.md"
    - "test-0006-server_integration.md"
    - "result-0003-tools_integration.md"
    - "result-0004-server_integration.md"
```

[Return to Table of Contents](#table-of-contents)

---

## 12. Version History

| Version | Date       | Author          | Changes                                                      |
|---------|------------|-----------------|--------------------------------------------------------------|
| 1.0     | 2025-12-12 | Claude Desktop  | Initial issue creation from test failures                    |
| 1.1     | 2025-12-12 | Claude Desktop  | Issue resolved, verified via integration test suite (19/19)  |

[Return to Table of Contents](#table-of-contents)

---

**Copyright:** Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
