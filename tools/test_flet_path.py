#!/usr/bin/env python3
"""
Test script to show the installed location of the Flet package.
"""
import sys
from pathlib import Path

# Add parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    import flet
    print(f"Flet package location: {flet.__file__}")
except ImportError as e:
    print(f"Failed to import flet: {e}")
