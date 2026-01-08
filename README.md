# MCP sed/awk Server

Secure sed, awk, and diff text processing capabilities for Model Context Protocol servers.

## Overview

This FastMCP server provides LLMs with efficient file editing and analysis through controlled execution of Unix text processing utilities. Token-efficient operations complement grep functionality while enforcing strict security controls through input validation, directory whitelisting, and resource limits.

## Features

- **Pattern substitution** via sed with regex support
- **Text transformation** using awk field extraction and processing
- **File comparison** with unified diff output
- **Preview operations** for change verification before application
- **Directory whitelist** access control
- **Comprehensive validation** preventing command injection, path traversal, ReDoS attacks
- **Resource enforcement** (file size limits, timeouts, memory caps)
- **Audit logging** for security-relevant operations
- **Cross-platform support** (Linux GNU tools, macOS BSD tools)

## Requirements

- Python 3.9 or higher
- FastMCP 2.0+
- System binaries: `sed`, `awk`, `diff` (standard on Linux/macOS)
- Write permissions in target directories for sed operations

## Installation

**From GitHub:**

```bash
git clone https://github.com/William12556/mcp-sed-awk.git
cd mcp-sed-awk
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

**Configure in Claude Desktop:**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sed-awk-mcp": {
      "command": "/path/to/mcp-sed-awk/venv/bin/mcp-sed-awk",
      "args": [
        "--allowed-directory", "/Users/your-username/Documents",
        "--allowed-directory", "/Users/your-username/Projects"
      ]
    }
  }
}
```

**Note:** Replace `/path/to/mcp-sed-awk` with the actual installation path. Use the full path to the virtual environment's binary to ensure reliable execution.

Restart Claude Desktop to activate the server.

## Available Tools

1. **sed_substitute** - Pattern-based find-and-replace with automatic backup
2. **preview_sed** - Non-destructive change preview
3. **awk_transform** - Field extraction and text transformation
4. **diff_files** - File comparison with unified diff output
5. **list_allowed_directories** - Display accessible paths

## Documentation

**[User Guide](docs/user-guide.md)** - Installation, configuration, usage examples, and troubleshooting

## Project Status

Version 1.0.0 - Initial release

**Completed:**
- Design baseline (15 functional requirements, 15 non-functional requirements)
- Full test suite (100% pass rate: 51% unit test coverage, 19/19 integration tests)
- Security architecture (validation, path control, resource limits, audit logging)
- Platform abstraction (GNU/BSD compatibility layer)
- FastMCP integration (decorator-based tool definitions)

## Important Notice

**Actual fitness for purpose is not guaranteed.**

This project represents exploration of AI-supported software development using Claude Desktop and Claude Code from Anthropic, using an orchestration framework for systematic software development.

## Development

**Setup development environment:**

```bash
git clone https://github.com/William12556/mcp-sed-awk.git
cd mcp-sed-awk
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

**Run tests:**

```bash
# Unit tests with coverage
pytest tests/ --cov=src/sed_awk_mcp --cov-report=term-missing

# Integration tests only
pytest tests/integration/

# All tests with output capture
pytest tests/ -v
```

**Test artifacts:** Per project convention, pipe test results to `workspace/test/result/pytest-result.txt` using:

```bash
pytest tests/ | tee workspace/test/result/pytest-result.txt
```

## License

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
