Created: 2025 December 10

# Security Architecture and Threat Mitigation

## Table of Contents

1. [Overview](<#1.0 overview>)
2. [Threat Model](<#2.0 threat model>)
3. [Security Architecture](<#3.0 security architecture>)
4. [Input Validation](<#4.0 input validation>)
5. [Access Control](<#5.0 access control>)
6. [Resource Protection](<#6.0 resource protection>)
7. [Platform Security](<#7.0 platform security>)
8. [Audit and Logging](<#8.0 audit and logging>)
9. [Risk Assessment](<#9.0 risk assessment>)
10. [Security Best Practices](<#10.0 security best practices>)
11. [References](<#11.0 references>)

---

## 1.0 Overview

The sed-awk-diff MCP server provides enhanced file editing capabilities through execution of native sed, awk, and diff binaries. This design introduces security considerations that must be addressed through defense-in-depth strategies.

**Core Security Objective:** Enable powerful text processing capabilities while preventing unauthorized access, command injection, resource exhaustion, and data corruption.

**Security Model:** Multi-layered defense incorporating input validation, access control, resource limits, and audit logging.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Threat Model

### 2.1 Threat Actors

- **Malicious LLM Prompts:** Adversarial inputs attempting to exploit command execution
- **Compromised LLM Context:** Injection attacks via poisoned training data or context
- **Local User Exploitation:** Privilege escalation through MCP interface
- **Resource Exhaustion Attacks:** DoS via computationally expensive operations

### 2.2 Attack Surfaces

#### 2.2.1 Command Injection
Native binary execution (sed/awk/diff) exposes command injection risk through:
- Pattern strings containing shell metacharacters
- Unvalidated sed commands (e, r, w, q, Q, R, W)
- AWK system() and popen() functions
- Escape sequence exploitation

#### 2.2.2 Path Traversal
File access operations vulnerable to:
- Relative path attacks (../)
- Symbolic link exploitation
- Race conditions (TOCTOU)
- Unauthorized directory access

#### 2.2.3 Resource Exhaustion
Computational attacks via:
- Catastrophic regex backtracking (ReDoS)
- Large file processing
- Infinite loops in awk programs
- Memory exhaustion through hold space manipulation

#### 2.2.4 Data Corruption
Unintended file modification through:
- Malformed sed expressions
- AWK output redirection
- Failed operations without rollback

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Security Architecture

### 3.1 Defense-in-Depth Layers

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: Input Validation                          │
│ - Pattern complexity limits                        │
│ - Command/function blacklists                      │
│ - Metacharacter filtering                          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 2: Access Control                            │
│ - Directory whitelisting                           │
│ - Path canonicalization                            │
│ - Permission verification                          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 3: Resource Protection                       │
│ - Execution timeouts                               │
│ - File size limits                                 │
│ - CPU/memory constraints (Linux)                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 4: Safe Execution                            │
│ - No shell invocation (shell=False)                │
│ - Argument array (not string)                      │
│ - Process isolation                                │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 5: Error Recovery                            │
│ - Automatic backup creation                        │
│ - Rollback on failure                              │
│ - Transaction semantics                            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 6: Audit Trail                               │
│ - Operation logging                                │
│ - Security event tracking                          │
│ - Failure analysis                                 │
└─────────────────────────────────────────────────────┘
```

### 3.2 Security Principles

1. **Fail-Secure:** Default deny for all operations
2. **Least Privilege:** Minimal permissions required
3. **Defense-in-Depth:** Multiple independent security layers
4. **Audit Everything:** Comprehensive logging of security-relevant events
5. **No Trust:** Validate all inputs regardless of source

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Input Validation

### 4.1 Sed Pattern Validation

**Threat:** Command injection via sed expressions

**Mitigations:**

#### 4.1.1 Command Blacklist
```python
FORBIDDEN_SED_COMMANDS = {
    'e': 'execute shell command',
    'r': 'read file',
    'w': 'write file',
    'q': 'quit (side effects)',
    'Q': 'quit immediately',
    'R': 'read line from file',
    'W': 'write pattern space',
    'T': 'branch on failure',
    't': 'branch on success',
    'b': 'branch (complex control flow)',
    ':': 'label (complex control flow)'
}
```

**Why Read and Write Commands Are Blacklisted:**

The `r` and `w` commands are blacklisted to prevent bypass of the MCP server's access controls. While the server provides file editing capabilities, these must flow through controlled Python code that validates paths, canonicalizes locations, and enforces directory whitelisting.

**The Critical Distinction:**

The MCP server provides file editing through controlled Python interfaces:
- Path validation against directory whitelist (section 5.1)
- Path canonicalization preventing traversal (section 5.2)
- Automatic backup creation and rollback capability

The blacklisted `r` and `w` commands would allow sed scripts to read/write arbitrary files, completely bypassing these security controls.

**Security Boundary:**

```python
# SECURE - MCP server controls all I/O
sed_substitute(
    file_path="/allowed/data.txt",  # ← Validated by MCP
    pattern="s/old/new/",           # ← sed operates on pattern space only
    ...
)

# INSECURE - sed script controls I/O (blocked by validation)
sed_substitute(
    pattern="r /etc/passwd",        # ← Would bypass whitelist
    ...
)
```

**Attack Scenario Prevented:**

```
Malicious LLM prompt:
  "Use pattern: w /tmp/evil_script; e chmod +x /tmp/evil_script"

Without blacklist: 
  - sed writes arbitrary file
  - sed executes shell command
  - Complete security breach

With blacklist: 
  - Pattern validation rejects 'w' and 'e' commands
  - ValueError raised
  - Operation denied
```

**Design Philosophy:**

All file I/O occurs through MCP server's validated interfaces. Sed operates on **pattern space only** with no direct file system access. This enforces the security boundary:
- Python layer controls **what** files are accessed (access control)
- Sed layer controls **how** content is transformed (text processing)

The functionality objective is achieved through MCP tools (`sed_substitute`, `awk_process`, `diff_files`), not through sed's built-in file commands.

#### 4.1.2 Metacharacter Filtering
```python
SHELL_METACHARACTERS = {';', '|', '&', '$', '`', '\n', '\r', '\x00'}
```

**Rationale:** These characters enable shell command chaining, variable substitution, and command execution.

#### 4.1.3 Complexity Limits
```python
MAX_PATTERN_LENGTH = 1000        # Prevent excessive parsing
MAX_NESTING_DEPTH = 5            # Limit regex nesting
MAX_REPETITION_QUALIFIER = 1000  # Prevent {n,m} DoS
```

#### 4.1.4 ReDoS Protection
Detect catastrophic backtracking patterns:
- Nested quantifiers: `(a+)+`, `(a*)*`
- Alternation explosion: `(a|b|c|d){10,100}`
- Excessive repetition: `a{1000,10000}`

### 4.2 AWK Program Validation

**Threat:** Shell command execution via AWK functions

**Mitigations:**

#### 4.2.1 Function Blacklist
```python
FORBIDDEN_AWK_FUNCTIONS = {
    'system': 'execute shell command',
    'popen': 'open pipe',
    'getline': 'read input (potential DoS)',
    'close': 'file operations',
    'fflush': 'file operations'
}
```

#### 4.2.2 Shell Pattern Detection
```python
shell_patterns = [
    r'\|',              # Pipe operator
    r'system\s*\(',     # system() call
    r'print\s+.*\|\s*'  # Print to pipe
]
```

### 4.3 Address Range Validation

**Threat:** Arbitrary line access, complex sed scripts

**Mitigation:** Whitelist-only address formats:
- Single line: `5`
- Line range: `1,10`
- Relative range: `1,+5`
- Last line: `$`

**Rejected:** Pattern addresses, complex expressions

### 4.4 Field Separator Validation

**Threat:** Code injection via AWK field separator

**Mitigation:**
- Maximum length: 10 characters
- No shell metacharacters
- Simple regex only

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Access Control

### 5.1 Directory Whitelisting

**Threat:** Unauthorized file system access

**Architecture:**
```python
class PathValidator:
    def __init__(self, allowed_directories: List[str]):
        self.allowed_paths = [Path(d).resolve() for d in allowed_directories]
    
    def validate(self, file_path: str) -> tuple[bool, Optional[str], Optional[Path]]:
        resolved = Path(file_path).resolve()
        for allowed in self.allowed_paths:
            try:
                resolved.relative_to(allowed)
                return True, None, resolved
            except ValueError:
                continue
        return False, "Access denied", None
```

### 5.2 Path Canonicalization

**Threat:** Path traversal via `.., symlinks, relative paths

**Mitigation:** `Path.resolve()` converts to absolute canonical path:
- Resolves symbolic links
- Eliminates `.` and `..` components
- Produces absolute path

**Example:**
```
Input:  "/allowed/../../etc/passwd"
Resolve: "/etc/passwd"
Validate: DENIED (not under /allowed)
```

### 5.3 TOCTOU Prevention

**Threat:** Race condition between path check and file access

**Mitigation:**
1. Resolve path once
2. Use resolved path for all operations
3. No additional path operations after validation

### 5.4 Configuration Sources

Directory whitelist configured via (priority order):
1. Environment variable: `ALLOWED_DIRECTORIES="/path1:/path2"`
2. Config file: `~/.config/sed-awk-mcp/allowed_dirs.txt`
3. Default: Current working directory only

**Security Note:** Config file must have restrictive permissions (0600)

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Resource Protection

### 6.1 Execution Timeouts

**Threat:** Infinite loops, catastrophic backtracking

**Mitigation:**
```python
subprocess.run(
    cmd,
    timeout=TIMEOUT_SECONDS,  # Default: 30s
    ...
)
```

**Timeout Values:**
- sed operations: 30 seconds
- awk operations: 30 seconds
- diff operations: 30 seconds

### 6.2 File Size Limits

**Threat:** Memory exhaustion, excessive processing time

**Mitigation:**
```python
MAX_FILE_SIZE = 10_000_000  # 10MB

if path.stat().st_size > MAX_FILE_SIZE:
    raise ValueError("File exceeds maximum size")
```

### 6.3 Linux Resource Limits

**Threat:** CPU/memory exhaustion

**Mitigation (Linux only):**
```python
import resource

def set_process_limits():
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))        # CPU time
    resource.setrlimit(resource.RLIMIT_AS, (100_000_000, 100_000_000))  # Memory
    resource.setrlimit(resource.RLIMIT_FSIZE, (50_000_000, 50_000_000))  # Output size

subprocess.run(
    cmd,
    preexec_fn=set_process_limits,
    ...
)
```

### 6.4 Single-File Operations

**Threat:** Batch operation amplification attacks

**Mitigation:** Each tool processes exactly one file per invocation:
- Limits blast radius of malicious operations
- Simplifies error handling and rollback
- Enables fine-grained access control

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Platform Security

### 7.1 Supported Platforms

- **Primary:** Linux (GNU tools)
- **Secondary:** macOS (BSD tools)

### 7.2 Binary Verification

**Threat:** Missing or compromised binaries

**Mitigation:**
```python
import shutil

required_binaries = ['sed', 'awk', 'diff']
for binary in required_binaries:
    if not shutil.which(binary):
        raise RuntimeError(f"Missing required binary: {binary}")
```

### 7.3 Platform-Specific Handling

#### 7.3.1 GNU sed vs BSD sed

**Difference:** In-place editing syntax

```bash
# GNU sed
sed -i.bak 's/pattern/replacement/' file

# BSD sed
sed -i .bak 's/pattern/replacement/' file
```

**Detection:**
```python
result = subprocess.run(['sed', '--version'], capture_output=True)
if 'GNU sed' in result.stdout:
    sed_type = 'gnu'
else:
    sed_type = 'bsd'
```

#### 7.3.2 GNU awk vs BSD awk

**Differences:**
- Function availability
- Regex dialect
- Extension features

**Mitigation:** Use POSIX-compatible AWK features only

### 7.4 Shell Invocation

**CRITICAL:** Never use `shell=True`

```python
# VULNERABLE
subprocess.run(f"sed 's/{pattern}/replacement/' {file}", shell=True)

# SECURE
subprocess.run(['sed', f's/{pattern}/replacement/', file], shell=False)
```

**Rationale:** `shell=True` enables:
- Command injection
- Shell metacharacter interpretation
- Environment variable expansion
- Subshell execution

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Audit and Logging

### 8.1 Security Event Logging

**Events requiring audit:**
- Path validation failures
- Pattern validation failures
- Operation timeouts
- File access denials
- Binary execution errors

### 8.2 Log Format

```python
{
    'timestamp': '2025-12-10T14:32:01.123Z',
    'operation': 'sed_substitute',
    'file': '/path/to/file',
    'pattern': 'truncated_pattern...',
    'user': 'mcp_client_id',
    'success': false,
    'error': 'Pattern contains forbidden character'
}
```

### 8.3 Context Logging

Operations use FastMCP Context for user-facing logging:
```python
await ctx.info(f"Executing sed on {file_path}")
await ctx.error(f"Pattern validation failed: {error}")
```

### 8.4 Sensitive Data Handling

**Risk:** Patterns may contain sensitive data

**Mitigation:**
- Truncate logged patterns (100 characters max)
- No full file content in logs
- Secure log file permissions (0600)

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Risk Assessment

### 9.1 Residual Risks

| Risk | Severity | Likelihood | Mitigation | Acceptance |
|------|----------|------------|------------|------------|
| Zero-day in sed/awk | High | Low | Timeouts, resource limits | Accept |
| Regex implementation bug | Medium | Low | Timeout, validation | Accept |
| TOCTOU race condition | Medium | Very Low | Path caching | Accept |
| Platform-specific exploit | Medium | Low | Binary verification | Accept |
| Configuration tampering | High | Low | File permissions, env vars | Accept with monitoring |

### 9.2 Attack Scenarios

#### 9.2.1 Command Injection Attempt
```
Input: pattern = "; rm -rf /"
Validation: BLOCKED - semicolon is forbidden character
Result: ValueError raised, operation denied
```

#### 9.2.2 Path Traversal Attempt
```
Input: file_path = "/allowed/../../../etc/passwd"
Validation: Path.resolve() = "/etc/passwd"
Check: Not within /allowed
Result: PermissionError raised, operation denied
```

#### 9.2.3 ReDoS Attempt
```
Input: pattern = "(a+)+(b+)+"
Validation: Detected nested quantifiers
Result: ValueError raised, operation denied
```

#### 9.2.4 Resource Exhaustion Attempt
```
Input: 100MB file + complex pattern
Validation: File size > MAX_FILE_SIZE
Result: ValueError raised before processing
```

### 9.3 Security Assumptions

1. **Trusted LLM:** Assumes LLM is not actively adversarial
2. **Host Security:** Assumes underlying OS is properly secured
3. **Binary Integrity:** Assumes sed/awk/diff binaries are authentic
4. **File System:** Assumes POSIX-compliant file system
5. **Single Tenant:** Assumes single user per MCP server instance

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Security Best Practices

### 10.1 Deployment

1. **Minimal Whitelist:** Only include necessary directories
2. **Read-Only When Possible:** Use diff/awk for analysis, sed only when editing required
3. **Backup Strategy:** Always enable backup=True for sed operations
4. **Log Monitoring:** Review audit logs for suspicious patterns
5. **Update Binaries:** Keep sed/awk/diff updated to latest versions

### 10.2 Configuration

```bash
# Restrictive directory whitelist
export ALLOWED_DIRECTORIES="/home/user/projects:/home/user/docs"

# Secure config file
mkdir -p ~/.config/sed-awk-mcp
chmod 700 ~/.config/sed-awk-mcp
cat > ~/.config/sed-awk-mcp/allowed_dirs.txt << EOF
/home/user/projects
/home/user/docs
EOF
chmod 600 ~/.config/sed-awk-mcp/allowed_dirs.txt
```

### 10.3 Operational Security

1. **Principle of Least Privilege:** Run MCP server as unprivileged user
2. **Network Isolation:** Use stdio transport for local-only access
3. **Regular Audits:** Review security logs weekly
4. **Incident Response:** Document procedure for security events
5. **Update Validation:** Test security after library updates

### 10.4 Integration with grep MCP

**Recommended Workflow:**
1. Use grep MCP to identify target files
2. Preview changes with `preview_sed` tool
3. Review diff output
4. Apply changes with `sed_substitute`
5. Verify results with `diff_files`

**Security Benefit:** grep narrows scope before potentially destructive operations

[Return to Table of Contents](<#table of contents>)

---

## 11.0 References

### 11.1 Standards and Guidelines

- OWASP Command Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- CWE-78: Improper Neutralization of Special Elements used in an OS Command: https://cwe.mitre.org/data/definitions/78.html
- CWE-22: Improper Limitation of a Pathname to a Restricted Directory: https://cwe.mitre.org/data/definitions/22.html
- ReDoS (Regular Expression Denial of Service): https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS

### 11.2 Tool Documentation

- GNU sed Manual: https://www.gnu.org/software/sed/manual/sed.html
- GNU awk Manual: https://www.gnu.org/software/gawk/manual/gawk.html
- POSIX Utilities: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/contents.html

### 11.3 FastMCP Resources

- FastMCP Documentation: https://gofastmcp.com
- Model Context Protocol Specification: https://modelcontextprotocol.io

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | William Watson | Initial security architecture documentation |
| 1.1 | 2025-12-10 | William Watson | Enhanced section 4.1.1 with detailed explanation of read/write command blacklist rationale |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
