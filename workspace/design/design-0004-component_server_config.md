Created: 2025 December 10

# Component Design: Server Configuration

## Document Information

**Document ID:** design-0004-component_server_config
**Document Type:** Component Design (Tier 3)
**Parent Domain:** [design-0004-domain_server](<design-0004-domain_server.md>)
**Status:** Draft
**Version:** 1.0
**Author:** William Watson
**Date:** 2025-12-10

## Table of Contents

1. [Component Information](<#1.0 component information>)
2. [Implementation](<#2.0 implementation>)
3. [Testing](<#3.0 testing>)

---

## 1.0 Component Information

**Component Name:** Server Configuration

**Purpose:** Parse and validate configuration from CLI arguments and environment variables.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation

```python
import os
from typing import List

def parse_arguments(args: List[str]) -> List[str]:
    """Parse configuration with priority: CLI → ENV → Default.
    
    Args:
        args: sys.argv[1:] command-line arguments
        
    Returns:
        List of allowed directory paths
        
    Raises:
        ValueError: If configuration invalid
    """
    # Priority 1: CLI arguments
    if args:
        return args
    
    # Priority 2: Environment variable
    env_dirs = os.environ.get('ALLOWED_DIRECTORIES', '')
    if env_dirs:
        return env_dirs.split(':')
    
    # Priority 3: Default to current directory
    return [os.getcwd()]
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Testing

```python
def test_cli_arguments():
    """CLI args take priority."""
    result = parse_arguments(['/tmp/a', '/tmp/b'])
    
    assert result == ['/tmp/a', '/tmp/b']

def test_environment_variable(monkeypatch):
    """ENV var used if no CLI args."""
    monkeypatch.setenv('ALLOWED_DIRECTORIES', '/tmp/x:/tmp/y')
    
    result = parse_arguments([])
    
    assert result == ['/tmp/x', '/tmp/y']

def test_default_cwd(monkeypatch):
    """Default to current directory."""
    monkeypatch.delenv('ALLOWED_DIRECTORIES', raising=False)
    
    result = parse_arguments([])
    
    assert result == [os.getcwd()]

def test_priority_order(monkeypatch):
    """CLI takes priority over ENV."""
    monkeypatch.setenv('ALLOWED_DIRECTORIES', '/tmp/env')
    
    result = parse_arguments(['/tmp/cli'])
    
    assert result == ['/tmp/cli']
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
