Created: 2025 December 10

# Component Design: PlatformConfig

## Document Information

**Document ID:** design-0002-component_platform_config
**Document Type:** Component Design (Tier 3)
**Parent Domain:** [design-0002-domain_platform](<design-0002-domain_platform.md>)
**Status:** Draft
**Version:** 1.0
**Author:** William Watson
**Date:** 2025-12-10

## Table of Contents

1. [Component Information](<#1.0 component information>)
2. [Implementation Details](<#2.0 implementation details>)
3. [Interfaces](<#3.0 interfaces>)
4. [Processing Logic](<#4.0 processing logic>)
5. [Error Handling](<#5.0 error handling>)
6. [Testing Requirements](<#6.0 testing requirements>)

---

## 1.0 Component Information

**Component Name:** PlatformConfig

**Purpose:** Detect platform (GNU/BSD), locate binaries, normalize command arguments for platform-specific execution.

**Responsibilities:**
- Binary location (sed, awk, diff)
- GNU vs BSD detection
- Argument normalization
- Binary path caching

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation Details

```python
import shutil
import subprocess
from typing import List, Dict

class PlatformConfig:
    """Platform-specific configuration and argument normalization."""
    
    def __init__(self) -> None:
        """Initialize platform detection and binary location."""
        self.sed_path = self._locate_binary('sed')
        self.awk_path = self._locate_binary('awk')
        self.diff_path = self._locate_binary('diff')
        self.is_gnu_sed = self._detect_gnu_sed()
    
    def normalize_sed_args(self, args: List[str]) -> List[str]:
        """Normalize sed arguments for platform.
        
        GNU: sed -i.bak 's/a/b/' file
        BSD: sed -i .bak 's/a/b/' file
        """
        
    def normalize_awk_args(self, args: List[str]) -> List[str]:
        """Normalize awk arguments (minimal platform differences)."""
        
    def normalize_diff_args(self, args: List[str]) -> List[str]:
        """Normalize diff arguments."""
    
    @property
    def binaries(self) -> Dict[str, str]:
        """Return binary paths."""
        return {
            'sed': self.sed_path,
            'awk': self.awk_path,
            'diff': self.diff_path
        }
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Interfaces

```python
def __init__(self) -> None:
    """Initialize with binary detection.
    
    Raises:
        BinaryNotFoundError: If required binary missing
    """

def normalize_sed_args(self, args: List[str]) -> List[str]:
    """Normalize sed arguments.
    
    Handles -i flag differences:
    - GNU: -i.bak (concatenated)
    - BSD: -i .bak (separate)
    
    Returns:
        Platform-normalized argument list
    """

def normalize_awk_args(self, args: List[str]) -> List[str]:
    """Normalize awk arguments.
    
    AWK has minimal platform differences.
    Currently returns args unchanged.
    """

def normalize_diff_args(self, args: List[str]) -> List[str]:
    """Normalize diff arguments.
    
    Diff syntax consistent across platforms.
    Currently returns args unchanged.
    """
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Processing Logic

### 4.1 Binary Location

```python
def _locate_binary(self, name: str) -> str:
    """Locate binary in PATH."""
    path = shutil.which(name)
    if not path:
        raise BinaryNotFoundError(f"{name} not found in PATH")
    return path
```

### 4.2 GNU Detection

```python
def _detect_gnu_sed(self) -> bool:
    """Detect if sed is GNU variant."""
    try:
        result = subprocess.run(
            [self.sed_path, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return 'GNU sed' in result.stdout
    except (subprocess.TimeoutExpired, OSError):
        return False  # Assume BSD if detection fails
```

### 4.3 Sed Argument Normalization

```python
def normalize_sed_args(self, args: List[str]) -> List[str]:
    """Normalize sed in-place editing arguments."""
    normalized = []
    i = 0
    
    while i < len(args):
        arg = args[i]
        
        if arg.startswith('-i'):
            if self.is_gnu_sed:
                # GNU: -i.bak or -i.ext
                if len(arg) == 2:  # Just "-i"
                    normalized.append('-i.bak')
                else:  # -i.ext
                    normalized.append(arg)
            else:  # BSD
                # BSD: -i followed by .ext
                normalized.append('-i')
                if len(arg) == 2:  # Just "-i"
                    normalized.append('.bak')
                else:  # -iext
                    normalized.append(arg[2:])
        else:
            normalized.append(arg)
        
        i += 1
    
    return normalized
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Error Handling

```python
class BinaryNotFoundError(Exception):
    """Raised when required binary not found."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
```

**Error Scenarios:**
```python
# Missing sed
BinaryNotFoundError("sed not found in PATH")

# Missing awk
BinaryNotFoundError("awk not found in PATH")

# Missing diff
BinaryNotFoundError("diff not found in PATH")
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Testing Requirements

```python
def test_binary_location():
    """Should locate binaries in PATH."""
    config = PlatformConfig()
    
    assert config.sed_path
    assert config.awk_path
    assert config.diff_path

def test_gnu_detection():
    """Should detect GNU sed correctly."""
    config = PlatformConfig()
    
    # Result depends on platform
    assert isinstance(config.is_gnu_sed, bool)

def test_sed_normalization_gnu():
    """GNU sed argument normalization."""
    config = PlatformConfig()
    config.is_gnu_sed = True
    
    # -i without suffix
    args = ['-i', 's/a/b/', 'file.txt']
    normalized = config.normalize_sed_args(args)
    assert normalized == ['-i.bak', 's/a/b/', 'file.txt']

def test_sed_normalization_bsd():
    """BSD sed argument normalization."""
    config = PlatformConfig()
    config.is_gnu_sed = False
    
    # -i without suffix
    args = ['-i', 's/a/b/', 'file.txt']
    normalized = config.normalize_sed_args(args)
    assert normalized == ['-i', '.bak', 's/a/b/', 'file.txt']

def test_missing_binary():
    """Should raise error if binary missing."""
    with patch('shutil.which', return_value=None):
        with pytest.raises(BinaryNotFoundError, match="sed not found"):
            PlatformConfig()
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
