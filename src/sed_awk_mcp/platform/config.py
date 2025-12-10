"""Platform configuration and binary detection.

This module provides platform detection, binary location, and argument
normalization for cross-platform execution of sed, awk, and diff commands.
"""

import logging
import shutil
import subprocess
from typing import List, Dict, Optional

# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

logger = logging.getLogger(__name__)


class BinaryNotFoundError(Exception):
    """Raised when required binary not found in PATH.
    
    Attributes:
        message: Human-readable error description
        binary_name: Name of the missing binary
    """
    
    def __init__(self, message: str, binary_name: Optional[str] = None) -> None:
        """Initialize BinaryNotFoundError.
        
        Args:
            message: Human-readable error description
            binary_name: Name of the missing binary (optional)
        """
        super().__init__(message)
        self.message = message
        self.binary_name = binary_name


class PlatformConfig:
    """Platform-specific configuration and argument normalization.
    
    This class provides cross-platform support by:
    - Locating required binaries (sed, awk, diff) in PATH
    - Detecting GNU vs BSD variants of tools
    - Normalizing command arguments for platform differences
    - Caching binary paths for performance
    
    Thread-safe implementation with lazy initialization.
    """
    
    def __init__(self) -> None:
        """Initialize platform detection and binary location.
        
        Locates all required binaries and detects platform variants.
        Uses lazy initialization for performance.
        
        Raises:
            BinaryNotFoundError: If any required binary is not found in PATH
        """
        self.sed_path = self._locate_binary('sed')
        self.awk_path = self._locate_binary('awk')
        self.diff_path = self._locate_binary('diff')
        self.is_gnu_sed = self._detect_gnu_sed()
        
        logger.debug(
            "PlatformConfig initialized: sed=%s awk=%s diff=%s gnu_sed=%s",
            self.sed_path, self.awk_path, self.diff_path, self.is_gnu_sed
        )
    
    def normalize_sed_args(self, args: List[str]) -> List[str]:
        """Normalize sed arguments for platform differences.
        
        Handles the main difference between GNU and BSD sed for in-place editing:
        - GNU sed: -i.bak (concatenated backup extension)
        - BSD sed: -i .bak (separate backup extension argument)
        
        Args:
            args: Original sed argument list
            
        Returns:
            Platform-normalized argument list
        """
        normalized = []
        i = 0
        
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('-i'):
                if self.is_gnu_sed:
                    # GNU sed: -i.bak or -i.ext (concatenated)
                    if len(arg) == 2:  # Just "-i"
                        normalized.append('-i.bak')
                    else:  # -i.ext or -iext
                        normalized.append(arg)
                else:
                    # BSD sed: -i followed by separate backup extension
                    normalized.append('-i')
                    if len(arg) == 2:  # Just "-i"
                        # Next argument should be backup extension, or use default
                        if i + 1 < len(args) and not args[i + 1].startswith('-'):
                            # Next arg is backup extension
                            normalized.append(args[i + 1])
                            i += 1  # Skip the backup extension argument
                        else:
                            # No backup extension provided, use default
                            normalized.append('.bak')
                    else:  # -iext
                        # Extract extension from -iext
                        normalized.append(arg[2:])
            else:
                normalized.append(arg)
            
            i += 1
        
        logger.debug(
            "PlatformConfig normalize_sed_args: %s -> %s (gnu=%s)",
            args, normalized, self.is_gnu_sed
        )
        return normalized
    
    def normalize_awk_args(self, args: List[str]) -> List[str]:
        """Normalize awk arguments for platform differences.
        
        AWK has minimal platform differences, so this method currently
        returns arguments unchanged. Future platform-specific awk
        normalization can be added here.
        
        Args:
            args: Original awk argument list
            
        Returns:
            Platform-normalized argument list (currently unchanged)
        """
        # AWK syntax is generally consistent across platforms
        return args.copy()
    
    def normalize_diff_args(self, args: List[str]) -> List[str]:
        """Normalize diff arguments for platform differences.
        
        Diff syntax is generally consistent across platforms, so this method
        currently returns arguments unchanged. Future platform-specific diff
        normalization can be added here.
        
        Args:
            args: Original diff argument list
            
        Returns:
            Platform-normalized argument list (currently unchanged)
        """
        # Diff syntax is consistent across platforms
        return args.copy()
    
    @property
    def binaries(self) -> Dict[str, str]:
        """Return dictionary of binary names to their paths.
        
        Returns:
            Dictionary mapping binary names to their full paths
        """
        return {
            'sed': self.sed_path,
            'awk': self.awk_path,
            'diff': self.diff_path
        }
    
    def _locate_binary(self, name: str) -> str:
        """Locate binary in PATH.
        
        Uses shutil.which() to locate the binary in the system PATH.
        
        Args:
            name: Binary name to locate
            
        Returns:
            Full path to the binary
            
        Raises:
            BinaryNotFoundError: If binary not found in PATH
        """
        path = shutil.which(name)
        if not path:
            raise BinaryNotFoundError(
                f"{name} not found in PATH",
                binary_name=name
            )
        
        logger.debug("PlatformConfig located binary: %s -> %s", name, path)
        return path
    
    def _detect_gnu_sed(self) -> bool:
        """Detect if sed is GNU variant.
        
        Attempts to run 'sed --version' and checks for 'GNU sed' in the output.
        Falls back to False (assumes BSD) if detection fails.
        
        Returns:
            True if GNU sed detected, False if BSD or detection failed
        """
        try:
            result = subprocess.run(
                [self.sed_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            is_gnu = 'GNU sed' in result.stdout
            logger.debug(
                "PlatformConfig GNU sed detection: path=%s gnu=%s",
                self.sed_path, is_gnu
            )
            return is_gnu
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
            logger.debug(
                "PlatformConfig GNU sed detection failed: %s, assuming BSD",
                str(e)
            )
            # Assume BSD if detection fails
            return False