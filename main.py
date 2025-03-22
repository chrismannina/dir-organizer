#!/usr/bin/env python3
"""
DEPRECATED: This is a backwards compatibility wrapper.
Please use the 'llm-organizer' command after installation instead.
"""

import os
import sys
import warnings

# Show deprecation warning
warnings.warn(
    "This script is deprecated and will be removed in a future version. "
    "Please use the 'llm-organizer' command after installation instead.",
    DeprecationWarning,
    stacklevel=2
)

# Add the src directory to the path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

# Import from the new package structure
from llm_organizer.__main__ import main

if __name__ == "__main__":
    main() 