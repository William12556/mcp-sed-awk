# System Test Execution Guide

**Test Document:** test-0007-system_mcp_integration.md  
**Date:** 2025-12-12  
**Platform:** MacOS Development Environment

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Server Configuration](#server-configuration)
4. [Test Execution Instructions](#test-execution-instructions)
5. [Results Documentation](#results-documentation)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

**Required Software:**
- Python 3.11+ with virtual environment
- Claude Desktop application
- sed, awk, diff binaries (standard on MacOS)
- Terminal application

**Project State:**
- Integration tests passing (19/19)
- Virtual environment activated
- Project installed in development mode

**Verify Prerequisites:**

```bash
# Check Python version
python3 --version  # Should show 3.11+

# Check binaries exist
which sed awk diff  # Should show paths to all three

# Verify project installation
cd /Users/williamwatson/Documents/GitHub/mcp-sed-awk
source venv/bin/activate
pip list | grep sed-awk-mcp  # Should show installed package
```

---

## Environment Setup

### Step 1: Prepare Test Directory

**Note:** Test files are located within the project repository at:
`/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test`

This directory is excluded from git via `.gitignore` and visible to Claude via Filesystem MCP tools.

```bash
# Navigate to test directory (already created)
cd /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test

# Verify directory contents
ls -la

# Set permissions if needed
chmod 755 /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test
```

### Step 2: Create Test Files

**Note:** Test files should already exist in the project test directory. If recreation needed:

```bash
# Navigate to test directory
cd /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test

# Create sample text file
echo "hello world" > sample.txt

# Create CSV file for awk testing
cat > data.csv << 'EOF'
name,age,city
Alice,30,NYC
Bob,25,LA
EOF

# Create files for diff testing
echo -e "version1\ndata" > old.txt
echo -e "version2\ndata" > new.txt

# Create file for preview testing
echo "test data" > preview.txt

# Create file for rollback testing
echo "original content" > rollback.txt

# Create large file for limit testing (>10MB)
dd if=/dev/zero of=large.txt bs=1048576 count=11

# Verify all files created
ls -lh
```

Expected output:
```
-rw-r--r--  1 user  wheel    56B Dec 12 10:00 data.csv
-rw-r--r--  1 user  wheel   11M Dec 12 10:00 large.txt
-rw-r--r--  1 user  wheel    13B Dec 12 10:00 old.txt
-rw-r--r--  1 user  wheel    13B Dec 12 10:00 new.txt
-rw-r--r--  1 user  wheel     9B Dec 12 10:00 preview.txt
-rw-r--r--  1 user  wheel    17B Dec 12 10:00 rollback.txt
-rw-r--r--  1 user  wheel    12B Dec 12 10:00 sample.txt
```

---

## Server Configuration

### Step 3: Configure MCP Server in Claude Desktop

**3.1: Open Claude Desktop Configuration**

```bash
# Open config file in editor
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**3.2: Add MCP Server Configuration**

Add this entry to the `mcpServers` section:

```json
{
  "mcpServers": {
    "sed-awk-mcp": {
      "command": "/Users/williamwatson/Documents/GitHub/mcp-sed-awk/venv/bin/python",
      "args": [
        "-m",
        "sed_awk_mcp.server",
        "/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test"
      ],
      "env": {}
    }
  }
}
```

**3.3: Save and Restart Claude Desktop**

```bash
# Save the config file (Cmd+S in editor)
# Quit Claude Desktop completely (Cmd+Q)
# Reopen Claude Desktop
```

**3.4: Verify Server Connection**

In Claude Desktop, look for:
- MCP icon showing "sed-awk-mcp" server connected
- No error messages in the interface

---

## Test Execution Instructions

### TC-039: Server Startup and Discovery

**Execution:**

1. In Claude Desktop, type:
   ```
   List all available MCP tools
   ```

2. **Expected Response:**
   - Claude lists 5 tools:
     - `sed_substitute`
     - `preview_sed`
     - `awk_transform`
     - `diff_files`
     - `list_allowed_directories`

3. **Verify Tool Descriptions:**
   ```
   Describe the sed_substitute tool
   ```

4. **Expected Response:**
   - Tool description shows parameters: file_path, pattern, replacement, line_range, create_backup

**Pass Criteria:** ✅ All 5 tools listed with descriptions

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-040: sed_substitute End-to-End Workflow

**Execution:**

1. In Claude Desktop, type:
   ```
   Use sed_substitute to replace "world" with "universe" in /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt
   ```

2. **Expected Response:**
   - Success message: "Successfully applied sed substitution to /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt, backup created at sample.txt.bak"

3. **Verify File Modified:**
   ```bash
   cat /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt
   ```
   Expected: `hello universe`

4. **Verify Backup Created:**
   ```bash
   cat /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt.bak
   ```
   Expected: `hello world`

**Pass Criteria:** ✅ File modified, backup exists, success message received

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-041: Security Validation - Path Traversal Prevention

**Execution:**

1. In Claude Desktop, type:
   ```
   Use sed_substitute to modify /etc/passwd by replacing "root" with "user"
   ```

2. **Expected Response:**
   - Error message containing "Access denied" or "not in allowed directories"
   - Operation should be refused

3. **Verify System File Unchanged:**
   ```bash
   # This should show original content (do not modify!)
   head -1 /etc/passwd
   ```

4. **Try Relative Path Attack:**
   ```
   Use sed_substitute on ../../etc/passwd
   ```

5. **Expected Response:**
   - Similar access denied error

**Pass Criteria:** ✅ Both attempts blocked, error messages clear, no file modifications

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-042: Security Validation - Command Injection Prevention

**Execution:**

1. **Test Command Substitution Injection:**
   ```
   Use sed_substitute to replace "test" with "$(rm -rf /)" in /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/rollback.txt
   ```

2. **Expected Response:**
   - ValidationError with message about forbidden pattern
   - Operation refused before execution

3. **Test Read Command Injection:**
   ```
   Use sed with pattern "r /etc/passwd" on /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/rollback.txt
   ```

4. **Expected Response:**
   - ValidationError about forbidden command

5. **Test Write Command Injection:**
   ```
   Use sed with pattern "w /tmp/evil" on /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/rollback.txt
   ```

6. **Expected Response:**
   - ValidationError about forbidden command

7. **Verify File Unchanged:**
   ```bash
   cat /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/rollback.txt
   ```
   Expected: `original content`

**Pass Criteria:** ✅ All three injection attempts blocked, file unchanged

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-043: GNU vs BSD sed Compatibility

**Execution:**

1. **Check Platform Detection:**
   ```bash
   # Check server logs for platform detection
   # Look for "GNU sed detected" or "BSD sed detected"
   ```

2. **Test Basic Substitution:**
   ```
   Use sed_substitute to replace "line1" with "LINE1" in /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt
   ```

3. **Verify Operation:**
   ```bash
   grep LINE1 /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/sample.txt
   ```

4. **Test with Backup:**
   ```
   Create another test file and perform substitution with backup
   ```

5. **Verify Backup Format:**
   ```bash
   ls /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/*.bak
   # Should show backup files regardless of sed variant
   ```

**Pass Criteria:** ✅ Operations work regardless of GNU/BSD sed

**Record Result:**
- [ ] PASS - Platform: _______ (GNU/BSD)
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-044: awk_transform Field Extraction

**Execution:**

1. In Claude Desktop, type:
   ```
   Use awk_transform to extract the age column (second field) from /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/data.csv using comma as separator
   ```

2. **Expected Response:**
   - Output contains: `age`, `30`, `25`

3. **Verify Original File Unchanged:**
   ```bash
   cat /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/data.csv
   ```
   Expected: Original CSV intact

**Pass Criteria:** ✅ Correct fields extracted, original file unchanged

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-045: diff_files Comparison

**Execution:**

1. In Claude Desktop, type:
   ```
   Use diff_files to compare /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/old.txt and /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/new.txt
   ```

2. **Expected Response:**
   - Unified diff format with:
     - `---` and `+++` headers
     - `@@` line markers
     - `-version1` and `+version2` changes

3. **Verify Files Unchanged:**
   ```bash
   cat /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/old.txt /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/new.txt
   ```
   Expected: Both files unchanged

**Pass Criteria:** ✅ Diff shows changes correctly, files preserved

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-046: preview_sed Non-Destructive Preview

**Execution:**

1. In Claude Desktop, type:
   ```
   Use preview_sed to show what would happen if I replace "test" with "TEST" in /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/preview.txt
   ```

2. **Expected Response:**
   - Diff showing `test` → `TEST` change

3. **Verify File Unchanged:**
   ```bash
   cat /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/preview.txt
   ```
   Expected: Still contains `test data` (lowercase)

4. **Verify No Backup:**
   ```bash
   ls /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/preview.txt.bak
   ```
   Expected: File does not exist

**Pass Criteria:** ✅ Preview shown, file unchanged, no backup

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-047: list_allowed_directories

**Execution:**

1. In Claude Desktop, type:
   ```
   Use list_allowed_directories to show which directories are accessible
   ```

2. **Expected Response:**
   - Shows `/Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test` (or its canonical path)
   - Path is absolute and resolved

**Pass Criteria:** ✅ Correct directory listed with canonical path

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-048: Error Recovery - Rollback on Failure

**Execution:**

1. **Note Current File Content:**
   ```bash
   cat /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/rollback.txt
   ```
   Expected: `original content`

2. **Attempt Invalid Operation:**
   ```
   Use sed_substitute with pattern "s/test/replacement/e" on /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/rollback.txt
   ```
   Note: The 'e' flag is forbidden

3. **Expected Response:**
   - ValidationError about forbidden flag

4. **Verify File Unchanged:**
   ```bash
   cat /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/rollback.txt
   ```
   Expected: Still `original content`

5. **Verify No Backup:**
   ```bash
   ls /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/rollback.txt.bak
   ```
   Expected: No backup (operation failed before backup stage)

**Pass Criteria:** ✅ Error returned, file unchanged, no corrupted state

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-049: Large File Rejection

**Execution:**

1. **Verify Large File Size:**
   ```bash
   ls -lh /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/large.txt
   ```
   Expected: Shows > 10M

2. **Attempt Operation:**
   ```
   Use sed_substitute to modify /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/large.txt
   ```

3. **Expected Response:**
   - ResourceError or similar error
   - Message mentions "exceeds limit" or "10MB"

4. **Verify File Unchanged:**
   ```bash
   ls -lh /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test/large.txt
   ```
   Expected: Same size (11M)

**Pass Criteria:** ✅ Operation refused, clear error message, file unchanged

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

### TC-050: Server Shutdown and Cleanup

**Execution:**

1. **Verify Server Running:**
   - Check Claude Desktop shows MCP connection active

2. **Initiate Shutdown:**
   - In Claude Desktop settings, disconnect sed-awk-mcp server
   - OR restart Claude Desktop

3. **Check for Clean Shutdown:**
   ```bash
   # Check for orphaned processes
   ps aux | grep sed_awk_mcp
   ```
   Expected: No processes running

4. **Verify No Temp Files:**
   ```bash
   # Check for temporary files in system temp
   find /tmp -name "*sed_preview*" 2>/dev/null
   ```
   Expected: No orphaned temp files

5. **Restart Server:**
   - Reopen Claude Desktop
   - Verify server reconnects

**Pass Criteria:** ✅ Clean shutdown, no orphaned resources, successful restart

**Record Result:**
- [ ] PASS
- [ ] FAIL - Document error message
- [ ] BLOCKED - Document reason

---

## Results Documentation

### Create Result Document

After completing all tests, document results:

```bash
cd /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/result
```

Create `result-0005-system_mcp_integration.md` with:

```yaml
result_info:
  id: "result-0005"
  title: "System Test Results - MCP Integration"
  date: "2025-12-12"
  executor: "Human"
  status: "passed" or "failed" or "partial"
  iteration: 1
  coupled_docs:
    test_ref: "test-0007"
    test_iteration: 1

summary:
  total_cases: 12
  passed: X
  failed: Y
  blocked: Z
  skipped: 0
  pass_rate: "XX%"

failures:
  - case_id: "TC-XXX"
    description: "..."
    error_output: "..."
```

---

## Troubleshooting

### Server Won't Start

**Problem:** Claude Desktop shows MCP connection error

**Solutions:**
1. Check config file syntax (valid JSON)
2. Verify Python path is correct:
   ```bash
   /Users/williamwatson/Documents/GitHub/mcp-sed-awk/venv/bin/python --version
   ```
3. Check directory exists:
   ```bash
   ls -la /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test
   ```
4. View Claude Desktop logs:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

### Tools Not Appearing

**Problem:** Claude Desktop doesn't show MCP tools

**Solutions:**
1. Restart Claude Desktop completely (Cmd+Q, then reopen)
2. Check server is in config file
3. Try asking explicitly: "What MCP tools are available?"

### Permission Denied Errors

**Problem:** Operations fail with permission errors

**Solutions:**
1. Check test directory permissions:
   ```bash
   chmod -R 755 /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test
   ```
2. Verify you own the files:
   ```bash
   ls -la /Users/williamwatson/Documents/GitHub/mcp-sed-awk/workspace/test/tmp/mcp-test
   ```

### Binary Not Found Errors

**Problem:** sed/awk/diff not detected

**Solutions:**
1. Verify binaries exist:
   ```bash
   which sed awk diff
   ```
2. Check PATH in server environment
3. Review server startup logs for binary detection

---

**End of Execution Guide**
