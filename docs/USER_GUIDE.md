Created: 2025 December 17

# MCP Sed-Awk User Guide

## Table of Contents

1. [Overview](<#1.0 overview>)
2. [Installation](<#2.0 installation>)
3. [Configuration](<#3.0 configuration>)
4. [Tool Reference](<#4.0 tool reference>)
5. [Usage Examples](<#5.0 usage examples>)
6. [Security Model](<#6.0 security model>)
7. [Error Handling](<#7.0 error handling>)
8. [Troubleshooting](<#8.0 troubleshooting>)
9. [Best Practices](<#9.0 best practices>)
10. [Glossary](<#10.0 glossary>)
11. [References](<#11.0 references>)

---

## 1.0 Overview

### 1.1 Purpose

The **mcp-sed-awk** server provides LLM-assisted text processing and file editing capabilities through controlled execution of Unix utilities (sed, awk, diff). Designed for token-efficient file operations that avoid loading entire file contents into LLM context.

### 1.2 Key Features

- **sed operations**: Pattern substitution with preview functionality
- **awk operations**: Field extraction and text transformation
- **diff operations**: File comparison with unified diff output
- **Security controls**: Directory whitelisting, input validation, resource limits
- **Platform support**: Linux (GNU tools) and macOS (BSD tools)
- **Audit logging**: Security-relevant operation tracking

### 1.3 System Requirements

**Python**: ≥3.9

**Required binaries**: sed, awk, diff (system-provided)

**Platforms**: Linux (GNU coreutils), macOS (BSD utilities)

**Dependencies**: FastMCP ≥0.1.0

### 1.4 Architecture

```
┌─────────────────────────────────────────┐
│         MCP Client (Claude Desktop)      │
└─────────────┬───────────────────────────┘
              │
              │ MCP Protocol
              ▼
┌─────────────────────────────────────────┐
│        FastMCP Server Framework          │
├─────────────────────────────────────────┤
│  Security Layer                          │
│  ├─ SecurityValidator (pattern checks)   │
│  ├─ PathValidator (whitelist)            │
│  └─ AuditLogger (security events)        │
├─────────────────────────────────────────┤
│  Platform Layer                          │
│  ├─ PlatformConfig (GNU/BSD detection)   │
│  └─ BinaryExecutor (controlled exec)     │
├─────────────────────────────────────────┤
│  Tool Layer                              │
│  ├─ sed_substitute / preview_sed         │
│  ├─ awk_transform                        │
│  ├─ diff_files                           │
│  └─ list_allowed_directories             │
└─────────────────────────────────────────┘
              │
              │ Validated execution
              ▼
┌─────────────────────────────────────────┐
│      System Binaries (sed/awk/diff)     │
└─────────────────────────────────────────┘
```

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Installation

### 2.1 From Source

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-sed-awk.git
cd mcp-sed-awk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### 2.2 From PyPI

```bash
pip install mcp-sed-awk
```

### 2.3 Verify Installation

```bash
# Verify package installation
pip list | grep mcp-sed-awk

# Verify binaries available
which sed awk diff
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Configuration

### 3.1 Claude Desktop Configuration

Edit Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sed-awk": {
      "command": "python",
      "args": ["-m", "sed_awk_mcp"],
      "env": {
        "ALLOWED_DIRECTORIES": "/path/to/workdir1:/path/to/workdir2",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3.2 Environment Variables

| Variable | Description | Default | Values |
|----------|-------------|---------|--------|
| `ALLOWED_DIRECTORIES` | Colon-separated list of accessible directories | Current directory | Absolute paths |
| `LOG_LEVEL` | Logging verbosity | INFO | DEBUG, INFO, WARNING, ERROR |

### 3.3 Configuration Validation

After configuring Claude Desktop:

1. Restart Claude Desktop application
2. Open new conversation
3. Verify server connection in MCP status indicator
4. Test with: "List allowed directories for sed-awk server"

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Tool Reference

### 4.1 sed_substitute

Perform in-place sed pattern substitution with backup and rollback.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Path to target file |
| `pattern` | string | Yes | Sed substitution pattern (e.g., `s/find/replace/g`) |
| `replacement` | string | Yes | Replacement string (for documentation) |
| `line_range` | string | No | Line range (e.g., `1,10` or `5,$`) |
| `create_backup` | boolean | No | Create `.bak` backup file (default: true) |

**Returns**: Confirmation message with operation details

**Example**:
```
Please use sed_substitute to replace "oldtext" with "newtext" in /path/to/file.txt
```

### 4.2 preview_sed

Preview sed substitution without modifying original file.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Path to target file |
| `pattern` | string | Yes | Sed substitution pattern |
| `replacement` | string | Yes | Replacement string |
| `line_range` | string | No | Line range |

**Returns**: Unified diff showing proposed changes, or "No changes"

**Example**:
```
Preview sed substitution of "old" to "new" in /path/to/file.txt
```

### 4.3 awk_transform

Apply AWK program for field extraction and text transformation.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Path to input file |
| `program` | string | Yes | AWK program (e.g., `{print $1}`) |
| `field_separator` | string | No | Field separator (default: whitespace) |
| `output_file` | string | No | Path for output (returns text if omitted) |

**Returns**: Transformed text or confirmation message

**Example**:
```
Use awk to extract the first column from /path/to/data.csv using comma separator
```

### 4.4 diff_files

Generate unified diff between two files.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file1_path` | string | Yes | Path to first file |
| `file2_path` | string | Yes | Path to second file |
| `context_lines` | integer | No | Context lines around changes (default: 3) |
| `ignore_whitespace` | boolean | No | Ignore whitespace differences (default: false) |

**Returns**: Unified diff output or empty string if identical

**Example**:
```
Show me the differences between version1.txt and version2.txt
```

### 4.5 list_allowed_directories

List directories accessible to MCP tools.

**Parameters**: None

**Returns**: Formatted list of allowed directory paths

**Example**:
```
What directories can the sed-awk server access?
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Usage Examples

### 5.1 Basic Text Substitution

**Scenario**: Replace all occurrences of "TODO" with "DONE" in a file.

**Prompt**:
```
Use sed to replace all instances of "TODO" with "DONE" in /home/user/project/tasks.txt
```

**Behind the scenes**:
```python
sed_substitute(
    file_path="/home/user/project/tasks.txt",
    pattern="s/TODO/DONE/g",
    replacement="DONE",
    create_backup=True
)
```

### 5.2 Preview Before Applying Changes

**Scenario**: Preview changes before applying them.

**Prompt**:
```
Show me what would change if I replace "old_function" with "new_function" 
in /home/user/code/main.py
```

**Behind the scenes**:
```python
preview_sed(
    file_path="/home/user/code/main.py",
    pattern="s/old_function/new_function/g",
    replacement="new_function"
)
```

### 5.3 Line-Range Substitution

**Scenario**: Replace text only in specific line range.

**Prompt**:
```
In /home/user/config.txt, replace "debug=true" with "debug=false" 
only in lines 10 through 20
```

**Behind the scenes**:
```python
sed_substitute(
    file_path="/home/user/config.txt",
    pattern="s/debug=true/debug=false/g",
    replacement="debug=false",
    line_range="10,20"
)
```

### 5.4 Field Extraction with AWK

**Scenario**: Extract specific columns from CSV data.

**Prompt**:
```
Extract the name and email columns (columns 1 and 3) from /data/users.csv
```

**Behind the scenes**:
```python
awk_transform(
    file_path="/data/users.csv",
    program='{print $1, $3}',
    field_separator=","
)
```

### 5.5 AWK with Output File

**Scenario**: Transform data and save to new file.

**Prompt**:
```
Use awk to sum the third column of /data/sales.csv and save results 
to /data/totals.txt
```

**Behind the scenes**:
```python
awk_transform(
    file_path="/data/sales.csv",
    program='{sum += $3} END {print sum}',
    field_separator=",",
    output_file="/data/totals.txt"
)
```

### 5.6 File Comparison

**Scenario**: Compare two configuration files.

**Prompt**:
```
Show me the differences between /config/prod.conf and /config/staging.conf
```

**Behind the scenes**:
```python
diff_files(
    file1_path="/config/prod.conf",
    file2_path="/config/staging.conf",
    context_lines=3
)
```

### 5.7 Ignoring Whitespace in Diff

**Scenario**: Compare files ignoring whitespace differences.

**Prompt**:
```
Compare script_v1.py and script_v2.py ignoring whitespace differences
```

**Behind the scenes**:
```python
diff_files(
    file1_path="/scripts/script_v1.py",
    file2_path="/scripts/script_v2.py",
    ignore_whitespace=True
)
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Security Model

### 6.1 Defense-in-Depth Architecture

The server implements multiple security layers:

```
User Request
    │
    ▼
┌─────────────────────────┐
│  Pattern Validation      │  ← Blocks dangerous sed/awk commands
│  (SecurityValidator)     │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Path Validation         │  ← Enforces directory whitelist
│  (PathValidator)         │    Prevents path traversal
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Resource Limits         │  ← File size: 10MB max
│                          │    Timeout: 30s max
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Controlled Execution    │  ← Python subprocess management
│  (BinaryExecutor)        │    No shell injection vectors
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Audit Logging           │  ← Security event tracking
│  (AuditLogger)           │
└─────────────────────────┘
```

### 6.2 Prohibited Operations

The security layer **blocks** these dangerous operations:

**Sed commands**:
- `r` (read file)
- `w` (write file)
- `e` (execute command)

**AWK functions**:
- `system()` (execute shell commands)
- `print >` (direct file writes)

**General**:
- Path traversal attempts (`../`, symbolic links)
- Access outside whitelisted directories
- Files exceeding 10MB
- Operations exceeding 30-second timeout

### 6.3 Directory Whitelisting

All file operations are restricted to configured `ALLOWED_DIRECTORIES`:

```json
{
  "env": {
    "ALLOWED_DIRECTORIES": "/home/user/projects:/home/user/documents"
  }
}
```

**Access granted**: `/home/user/projects/file.txt` ✓

**Access denied**: `/etc/passwd` ✗

**Access denied**: `/home/user/secret/file.txt` ✗

### 6.4 Backup and Rollback

The `sed_substitute` tool provides automatic safety mechanisms:

1. **Automatic backup**: Creates `.bak` file before modification
2. **Rollback on failure**: Restores original file if sed execution fails
3. **Atomic operations**: Changes applied in single sed invocation

### 6.5 Audit Logging

Security-relevant events are logged:

- Validation failures (blocked patterns, unauthorized paths)
- Successful tool executions
- Execution failures with error details
- File access attempts

Logs include timestamp, tool name, operation, file path, and outcome.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Error Handling

### 7.1 Error Types

| Error Class | Cause | Resolution |
|-------------|-------|------------|
| `ValidationError` | Forbidden sed/awk pattern | Use safe pattern without blocked commands |
| `SecurityError` | Path outside whitelist | Verify file path in allowed directories |
| `ResourceError` | File exceeds 10MB limit | Split large files or use alternative tools |
| `ExecutionError` | sed/awk/diff execution failure | Check pattern syntax, verify file format |
| `TimeoutError` | Operation exceeds 30s | Simplify operation or increase timeout |
| `FileNotFoundError` | Target file does not exist | Verify file path and existence |

### 7.2 Common Error Messages

**Pattern Validation Failure**:
```
ValidationError: Forbidden sed command 'e' in pattern 's/x/y/e'
```
**Resolution**: Remove the `e` flag which executes commands.

**Path Security Violation**:
```
SecurityError: Path /etc/passwd is outside allowed directories
```
**Resolution**: Configure whitelist to include required directory.

**Resource Limit Exceeded**:
```
ResourceError: File size 15728640 bytes exceeds limit of 10485760 bytes
```
**Resolution**: Process smaller files or request limit increase.

**Execution Failure**:
```
ExecutionError: Sed execution failed (exit code 1): unterminated `s' command
```
**Resolution**: Check sed pattern syntax.

### 7.3 Error Recovery

**For sed_substitute**:
- Automatic rollback restores original file from `.bak` backup
- Backup preserved even after rollback for manual recovery

**For preview_sed**:
- No data loss risk (read-only operation)
- Temporary files automatically cleaned up

**For awk_transform with output_file**:
- Original input file never modified
- Partial output file may exist on failure (safe to delete)

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Troubleshooting

### 8.1 Server Connection Issues

**Symptom**: MCP server not appearing in Claude Desktop

**Diagnosis**:
1. Check configuration file syntax (valid JSON)
2. Verify Python path in `command` field
3. Ensure package installed in correct Python environment

**Resolution**:
```bash
# Verify installation
pip list | grep mcp-sed-awk

# Test manual execution
python -m sed_awk_mcp
```

### 8.2 Tool Execution Failures

**Symptom**: Tool returns "Tools not initialized" error

**Cause**: Server initialization failed

**Resolution**:
1. Restart Claude Desktop
2. Check server logs for initialization errors
3. Verify `ALLOWED_DIRECTORIES` environment variable set

### 8.3 Pattern Syntax Issues

**Symptom**: sed pattern not matching expected text

**Diagnosis**:
1. Use `preview_sed` to verify pattern behavior
2. Check for special characters requiring escaping
3. Verify pattern type: basic vs. extended regex

**Resolution**:
```bash
# Test pattern manually
echo "test string" | sed 's/pattern/replacement/'
```

### 8.4 Platform Differences

**Symptom**: Tool works on macOS but fails on Linux (or vice versa)

**Cause**: GNU sed vs. BSD sed syntax differences

**Resolution**: Server automatically detects platform and normalizes arguments. Report persistent issues.

### 8.5 Permission Issues

**Symptom**: "Permission denied" errors

**Resolution**:
1. Verify file permissions: `ls -l /path/to/file`
2. Ensure user has write permission for sed_substitute
3. Check directory permissions for output files

### 8.6 Large File Processing

**Symptom**: "Resource limit exceeded" error

**Workaround**:
1. Split large files: `split -l 10000 largefile.txt chunk_`
2. Process chunks individually
3. Combine results: `cat chunk_* > result.txt`

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Best Practices

### 9.1 Always Preview First

Before applying destructive sed operations, use `preview_sed`:

```
# Good practice
1. Preview: "Preview replacing X with Y in file.txt"
2. Review diff output
3. Apply: "Apply sed substitution replacing X with Y in file.txt"

# Risky practice
"Replace all X with Y in file.txt" (no preview)
```

### 9.2 Leverage Automatic Backups

The `.bak` backup files enable recovery:

```bash
# After sed_substitute, backup exists
ls -la
# → file.txt
# → file.txt.bak

# Manual rollback if needed
cp file.txt.bak file.txt
```

### 9.3 Use Specific Line Ranges

Limit scope of changes to reduce risk:

```
# Precise
"Replace X with Y in lines 10-20 of file.txt"

# Risky
"Replace X with Y in entire file.txt"
```

### 9.4 Test AWK Programs Separately

Verify AWK logic before applying to critical files:

```bash
# Test on sample data
echo "col1,col2,col3" | awk -F, '{print $1, $3}'

# Then use in MCP tool
```

### 9.5 Understand Pattern Matching

**sed patterns** are line-oriented:
- `s/old/new/` replaces first occurrence per line
- `s/old/new/g` replaces all occurrences per line
- `s/^old/new/` replaces only at line start

**awk patterns** are record/field-oriented:
- Default record separator: newline
- Default field separator: whitespace
- Custom separators: `-F,` for CSV

### 9.6 Escape Special Characters

Characters with special meaning in sed/awk:

```
sed:  / \ . * [ ] ^ $ &
awk:  / \ . * [ ] ^ $ { } ( ) | +
```

Use backslash to escape: `s/\$variable/value/g`

### 9.7 Verify Directory Whitelist

Before file operations, confirm accessible directories:

```
"List allowed directories for sed-awk server"
```

### 9.8 Monitor Audit Logs

For security-critical environments, review audit logs periodically:

```bash
# Logs written to stderr (captured by Claude Desktop)
tail -f ~/.claude/logs/sed-awk-mcp.log
```

### 9.9 Handle Binary Files Appropriately

The server is designed for text files. For binary files:
- Use specialized tools (hexdump, strings, etc.)
- Convert to text format first if possible

### 9.10 Optimize AWK Performance

For large files, efficient AWK programs improve performance:

```awk
# Efficient: exit early when done
NR > 1000 { exit }

# Efficient: skip unnecessary processing
NF < 3 { next }

# Inefficient: unnecessary computation
{ for (i=1; i<=NF; i++) sum += $i }  # if only $3 needed
```

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Glossary

| Term | Definition |
|------|------------|
| **AWK** | Pattern scanning and text processing language for field-based operations |
| **sed** | Stream editor for filtering and transforming text line-by-line |
| **diff** | File comparison utility showing differences between files |
| **MCP** | Model Context Protocol - standard protocol for LLM tool/resource access |
| **FastMCP** | Python framework for building production-ready MCP servers |
| **Pattern** | Regular expression defining text to match/replace |
| **Field separator** | Character(s) used to split lines into fields (default: whitespace) |
| **Unified diff** | Standard diff format showing context around changes |
| **Whitelist** | Explicitly allowed set of directories for file access |
| **Path traversal** | Security attack attempting to access files outside allowed directories |
| **ReDoS** | Regular Expression Denial of Service - attack exploiting regex complexity |
| **Backup file** | Copy of original file with `.bak` extension created before modification |
| **Line range** | Specification of lines to operate on (e.g., `10,20` or `5,$`) |
| **Context lines** | Number of unchanged lines shown around changes in diff output |

[Return to Table of Contents](<#table of contents>)

---

## 11.0 References

### 11.1 Project Documentation

- [README.md](../README.md) - Project overview and quick start
- [security.md](security.md) - Detailed security architecture documentation
- [TEST_RESULTS_v0.1.0.md](TEST_RESULTS_v0.1.0.md) - Test coverage and validation results

### 11.2 Design Documentation

- [Master Design](../workspace/design/design-0000-master_sed-awk-mcp.md) - System architecture
- [Security Domain](../workspace/design/design-0001-domain_security.md) - Security layer design
- [Platform Domain](../workspace/design/design-0002-domain_platform.md) - Platform abstraction design
- [Tools Domain](../workspace/design/design-0003-domain_tools.md) - Tool implementation design
- [Server Domain](../workspace/design/design-0004-domain_server.md) - Server integration design

### 11.3 External Resources

**sed documentation**:
- GNU sed: https://www.gnu.org/software/sed/manual/
- BSD sed: https://man.freebsd.org/cgi/man.cgi?query=sed

**AWK documentation**:
- GNU awk: https://www.gnu.org/software/gawk/manual/
- POSIX awk: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/awk.html

**MCP Protocol**:
- Anthropic MCP Documentation: https://modelcontextprotocol.io/
- FastMCP Framework: https://github.com/jlowin/fastmcp

**Python Resources**:
- subprocess module: https://docs.python.org/3/library/subprocess.html
- pathlib module: https://docs.python.org/3/library/pathlib.html

### 11.4 Getting Help

**Issue Tracker**: https://github.com/yourusername/mcp-sed-awk/issues

**Questions**: Open discussion in repository Issues section

**Security Issues**: Report privately to project maintainer

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2025-12-17 | Initial user guide creation |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
