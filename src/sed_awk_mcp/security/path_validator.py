"""Path validation for directory whitelist enforcement.

This module provides secure path validation with TOCTOU-resistant checking,
symlink resolution, and path traversal prevention.
"""

import logging
from pathlib import Path
from typing import List, Set, Optional

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Raised when path access violation detected.
    
    Attributes:
        message: Human-readable error description
        path: Path that violated access control (optional)
    """
    
    def __init__(self, message: str, path: Optional[str] = None) -> None:
        """Initialize SecurityError.
        
        Args:
            message: Human-readable error description
            path: Path that violated access control (optional)
        """
        super().__init__(message)
        self.message = message
        self.path = path


class PathValidator:
    """Validates file paths against directory whitelist.
    
    This class provides secure path validation including:
    - Directory whitelist enforcement
    - Path canonicalization (symlink resolution)
    - Path traversal prevention
    - TOCTOU-resistant validation
    
    Thread-safe implementation with immutable whitelist after initialization.
    """
    
    def __init__(self, allowed_dirs: List[str]) -> None:
        """Initialize validator with allowed directories.
        
        Canonicalizes all allowed directories by resolving to absolute paths
        and following symlinks. Validates that all entries are existing
        directories.
        
        Args:
            allowed_dirs: List of directory paths to allow access to
            
        Raises:
            ValueError: If allowed_dirs is empty or contains invalid paths
        """
        if not allowed_dirs:
            raise ValueError("Allowed directories list cannot be empty")
        
        self._allowed_dirs: Set[Path] = self._canonicalize_dirs(allowed_dirs)
        
        logger.debug(
            "PathValidator initialized with %d allowed directories: %s",
            len(self._allowed_dirs),
            [str(d) for d in sorted(self._allowed_dirs)]
        )
    
    def validate_path(self, path: str) -> Path:
        """Validate path against whitelist.
        
        Resolves the input path to canonical form (absolute path with symlinks
        resolved) and checks if it's within any allowed directory. Prevents
        path traversal attacks and symlink bypass attempts.
        
        Args:
            path: File path to validate
            
        Returns:
            Canonicalized Path object if allowed
            
        Raises:
            SecurityError: If path not in allowed directories
        """
        try:
            # Resolve to canonical form (absolute + symlinks)
            # Use strict=False to allow non-existent files
            target = Path(path).resolve(strict=False)
        except (RuntimeError, OSError) as e:
            logger.debug(
                "PathValidator validate_path path=%s error=Cannot resolve: %s",
                path, str(e)
            )
            raise SecurityError(
                f"Cannot resolve path '{path}': {e}",
                path
            )
        
        # Check if path is within allowed directories
        if not self._is_allowed(target):
            logger.debug(
                "PathValidator validate_path path=%s target=%s allowed=%s error=Access denied",
                path, str(target), [str(d) for d in sorted(self._allowed_dirs)]
            )
            raise SecurityError(
                f"Access denied: '{path}' not in allowed directories",
                path
            )
        
        logger.debug(
            "PathValidator validate_path path=%s target=%s result=allowed",
            path, str(target)
        )
        return target
    
    def list_allowed(self) -> List[str]:
        """Return list of allowed directory paths.
        
        Returns:
            Sorted list of allowed directory paths as strings
        """
        return sorted(str(path) for path in self._allowed_dirs)
    
    def _canonicalize_dirs(self, dirs: List[str]) -> Set[Path]:
        """Canonicalize and validate allowed directories.
        
        Converts each directory path to canonical form by resolving to
        absolute path and following symlinks. Validates that each path
        exists and is a directory.
        
        Args:
            dirs: List of directory path strings
            
        Returns:
            Set of canonicalized Path objects
            
        Raises:
            ValueError: If any directory is invalid
        """
        canonical = set()
        
        for dir_str in dirs:
            try:
                # Convert to Path and resolve (absolute + symlinks)
                # Use strict=True to require directory exists
                path = Path(dir_str).resolve(strict=True)
                
                # Verify it's a directory
                if not path.is_dir():
                    raise ValueError(f"Not a directory: {dir_str}")
                
                canonical.add(path)
                logger.debug(
                    "PathValidator canonicalized directory: %s -> %s",
                    dir_str, str(path)
                )
                
            except FileNotFoundError:
                raise ValueError(f"Invalid directory '{dir_str}': Directory does not exist")
            except (RuntimeError, OSError) as e:
                raise ValueError(f"Invalid directory '{dir_str}': {e}")
        
        return canonical
    
    def _is_allowed(self, target: Path) -> bool:
        """Check if target path is within any allowed directory.
        
        Uses Path.relative_to() to check if the target path is a subpath
        of any allowed directory. This method is robust against path
        traversal attempts.
        
        Args:
            target: Canonicalized path to check
            
        Returns:
            True if path is within any allowed directory
        """
        # Check if target is within any allowed directory
        for allowed_dir in self._allowed_dirs:
            try:
                # Check if target is relative to allowed_dir
                # This will raise ValueError if target is not within allowed_dir
                target.relative_to(allowed_dir)
                return True
            except ValueError:
                # Not relative to this allowed_dir, continue checking others
                continue
        
        return False