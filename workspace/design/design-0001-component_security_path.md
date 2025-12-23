Created: 2025 December 10

# Component Design: PathValidator

## Document Information

**Document ID:** design-0001-component_security_path
**Document Type:** Component Design (Tier 3)
**Parent Domain:** [design-0001-domain_security](<design-0001-domain_security.md>)
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
6. [Data Structures](<#6.0 data structures>)
7. [Testing Requirements](<#7.0 testing requirements>)

---

## 1.0 Component Information

**Component Name:** PathValidator

**Purpose:** Enforce directory whitelist and prevent path traversal attacks through path canonicalization and access control.

**Responsibilities:**
- Whitelist management
- Path canonicalization (symlink resolution)
- Access control enforcement
- TOCTOU prevention

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Implementation Details

### 2.1 Class Definition

```python
from pathlib import Path
from typing import List, Set

class PathValidator:
    """Validates file paths against directory whitelist."""
    
    def __init__(self, allowed_dirs: List[str]) -> None:
        """Initialize validator with allowed directories.
        
        Args:
            allowed_dirs: List of allowed directory paths
            
        Raises:
            ValueError: If allowed_dirs is empty or contains invalid paths
        """
        self._allowed_dirs: Set[Path] = self._canonicalize_dirs(allowed_dirs)
    
    def validate_path(self, path: str) -> Path:
        """Validate path against whitelist.
        
        Args:
            path: File path to validate
            
        Returns:
            Canonicalized Path object if allowed
            
        Raises:
            SecurityError: If path not in allowed directories
        """
    
    def list_allowed(self) -> List[str]:
        """Return list of allowed directory paths.
        
        Returns:
            List of allowed directory paths as strings
        """
```

### 2.2 Key Elements

**Initialization:**
- Canonicalize allowed directories at initialization
- Resolve symlinks in allowed paths
- Store as set of Path objects for O(1) lookup

**Validation:**
- Resolve target path to absolute canonical form
- Check all parent directories against whitelist
- Prevent TOCTOU by validating immediately before use

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Interfaces

### 3.1 Public Methods

```python
def __init__(self, allowed_dirs: List[str]) -> None:
    """Initialize with whitelist.
    
    Canonicalizes all allowed directories:
    - Resolves to absolute paths
    - Resolves symlinks
    - Removes duplicates
    
    Args:
        allowed_dirs: List of directory paths
        
    Raises:
        ValueError: If list empty or paths invalid
    """

def validate_path(self, path: str) -> Path:
    """Validate and canonicalize path.
    
    Process:
    1. Convert to Path object
    2. Resolve to absolute path (Path.resolve())
    3. Check all parents against whitelist
    4. Return canonicalized Path if allowed
    
    Args:
        path: File path string
        
    Returns:
        Canonicalized Path object
        
    Raises:
        SecurityError: Path not in allowed directories
        FileNotFoundError: Path does not exist
    """

def list_allowed(self) -> List[str]:
    """Return whitelist as strings.
    
    Returns:
        Sorted list of allowed directory paths
    """
```

### 3.2 Internal Methods

```python
def _canonicalize_dirs(self, dirs: List[str]) -> Set[Path]:
    """Canonicalize allowed directories.
    
    Args:
        dirs: List of directory path strings
        
    Returns:
        Set of canonicalized Path objects
        
    Raises:
        ValueError: If invalid directory
    """

def _is_allowed(self, target: Path) -> bool:
    """Check if path is within allowed directories.
    
    Args:
        target: Canonicalized path to check
        
    Returns:
        True if path within allowed directories
    """
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Processing Logic

### 4.1 Initialization

```python
def __init__(self, allowed_dirs: List[str]) -> None:
    if not allowed_dirs:
        raise ValueError("Allowed directories list cannot be empty")
    
    self._allowed_dirs = self._canonicalize_dirs(allowed_dirs)

def _canonicalize_dirs(self, dirs: List[str]) -> Set[Path]:
    """Canonicalize and validate allowed directories."""
    canonical = set()
    
    for dir_str in dirs:
        try:
            # Convert to Path and resolve (absolute + symlinks)
            path = Path(dir_str).resolve(strict=True)
            
            # Verify it's a directory
            if not path.is_dir():
                raise ValueError(f"Not a directory: {dir_str}")
            
            canonical.add(path)
        except (FileNotFoundError, RuntimeError) as e:
            raise ValueError(f"Invalid directory '{dir_str}': {e}")
    
    return canonical
```

### 4.2 Path Validation

```python
def validate_path(self, path: str) -> Path:
    """Validate path against whitelist."""
    try:
        # Resolve to canonical form (absolute + symlinks)
        target = Path(path).resolve(strict=False)
    except (RuntimeError, OSError) as e:
        raise SecurityError(f"Cannot resolve path '{path}': {e}")
    
    # Check if path is within allowed directories
    if not self._is_allowed(target):
        raise SecurityError(
            f"Access denied: '{path}' not in allowed directories"
        )
    
    return target

def _is_allowed(self, target: Path) -> bool:
    """Check if target is within any allowed directory."""
    # Check target and all parents
    for allowed_dir in self._allowed_dirs:
        try:
            # Check if target is relative to allowed_dir
            target.relative_to(allowed_dir)
            return True
        except ValueError:
            # Not relative to this allowed_dir, continue
            continue
    
    return False
```

**Path Traversal Prevention:**
```python
# Example: User provides "../../../etc/passwd"
# 1. Path.resolve() converts to absolute: "/etc/passwd"
# 2. _is_allowed() checks if "/etc/passwd" is within any allowed directory
# 3. Fails because "/etc/passwd" not relative to any allowed directory
# 4. Raises SecurityError
```

**Symlink Handling:**
```python
# Example: User provides "link_to_sensitive_file"
# where link_to_sensitive_file -> /etc/passwd
# 1. Path.resolve() follows symlink: "/etc/passwd"
# 2. _is_allowed() checks "/etc/passwd" (not the link)
# 3. Fails because resolved path outside allowed directories
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Error Handling

### 5.1 Exception Types

```python
class SecurityError(Exception):
    """Raised when path access violation detected.
    
    Attributes:
        message: Human-readable error description
        path: Path that violated access control
    """
    
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.path = path
```

### 5.2 Error Scenarios

**Initialization errors:**
```python
# Empty whitelist
ValueError("Allowed directories list cannot be empty")

# Invalid directory
ValueError("Invalid directory '/nonexistent': [Errno 2] No such file or directory")

# Not a directory (is a file)
ValueError("Not a directory: /path/to/file.txt")
```

**Validation errors:**
```python
# Path outside whitelist
SecurityError("Access denied: '/etc/passwd' not in allowed directories")

# Path traversal attempt
SecurityError("Access denied: '../../../etc/passwd' not in allowed directories")

# Symlink to forbidden location
SecurityError("Access denied: 'link' not in allowed directories")
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Data Structures

### 6.1 Internal State

```python
class PathValidator:
    _allowed_dirs: Set[Path]
    # Set of canonicalized allowed directory paths
    # - Using set for O(1) membership testing
    # - Path objects are canonical (absolute + symlinks resolved)
    # - Immutable after initialization
```

### 6.2 Whitelist Structure

```
_allowed_dirs = {
    Path('/home/user/project'),
    Path('/tmp/workspace'),
    Path('/var/data/files')
}
```

**Benefits:**
- Fast lookup: O(1) membership test
- No duplicates: Set automatically deduplicates
- Canonical paths: Consistent comparison

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Testing Requirements

### 7.1 Unit Tests

```python
def test_valid_path():
    """Paths within allowed directories should pass."""
    validator = PathValidator(['/tmp/test'])
    
    # Direct file in allowed directory
    result = validator.validate_path('/tmp/test/file.txt')
    assert result == Path('/tmp/test/file.txt')
    
    # Subdirectory file
    result = validator.validate_path('/tmp/test/subdir/file.txt')
    assert result == Path('/tmp/test/subdir/file.txt')

def test_path_traversal_blocked():
    """Path traversal attempts should be blocked."""
    validator = PathValidator(['/tmp/test'])
    
    # Attempt to escape via ../
    with pytest.raises(SecurityError, match="not in allowed directories"):
        validator.validate_path('/tmp/test/../../etc/passwd')

def test_symlink_resolution():
    """Symlinks should be resolved and validated."""
    # Setup: Create symlink outside allowed directory
    os.symlink('/etc/passwd', '/tmp/test/link')
    
    validator = PathValidator(['/tmp/test'])
    
    # Symlink target outside allowed directories
    with pytest.raises(SecurityError):
        validator.validate_path('/tmp/test/link')

def test_absolute_path_normalization():
    """Relative and absolute paths should be normalized."""
    validator = PathValidator(['/tmp/test'])
    
    # Relative path
    os.chdir('/tmp')
    result = validator.validate_path('test/file.txt')
    assert result == Path('/tmp/test/file.txt')

def test_empty_whitelist():
    """Empty whitelist should raise ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        PathValidator([])

def test_invalid_directory():
    """Invalid directories should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid directory"):
        PathValidator(['/nonexistent'])

def test_file_as_allowed_dir():
    """Files in allowed_dirs should raise ValueError."""
    Path('/tmp/file.txt').touch()
    
    with pytest.raises(ValueError, match="Not a directory"):
        PathValidator(['/tmp/file.txt'])

def test_list_allowed():
    """list_allowed should return sorted whitelist."""
    validator = PathValidator(['/tmp/b', '/tmp/a', '/tmp/c'])
    
    allowed = validator.list_allowed()
    assert allowed == ['/tmp/a', '/tmp/b', '/tmp/c']
```

### 7.2 Security Tests

```python
def test_toctou_prevention():
    """Validator should check path at invocation time."""
    validator = PathValidator(['/tmp/test'])
    
    # Validate path
    path = validator.validate_path('/tmp/test/file.txt')
    
    # Change allowed directories (not possible - immutable)
    # This test verifies immutability
    with pytest.raises(AttributeError):
        validator._allowed_dirs = {Path('/etc')}

def test_case_sensitivity():
    """Path comparison should be case-sensitive on Linux."""
    validator = PathValidator(['/tmp/Test'])
    
    # Different case should fail
    with pytest.raises(SecurityError):
        validator.validate_path('/tmp/test/file.txt')
```

### 7.3 Integration Tests

**Scenarios:**
1. Tools Domain uses PathValidator before all file operations
2. Multiple paths validated in sequence
3. Error messages propagate to MCP client

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Description              |
| ------- | ---------- | ------------------------ |
| 1.0     | 2025-12-10 | Initial component design |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
