"""Test configuration for integration tests."""

import sys
from pathlib import Path

# Add src to path for all integration tests
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
