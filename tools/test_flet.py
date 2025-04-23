#!/usr/bin/env python3
"""
Test script to check Flet version and available attributes.
"""
import sys
from pathlib import Path

# Add parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    import flet
    print("Flet version:", flet.__version__)
    print("Available in flet module:", [item for item in dir(flet) if not item.startswith('_')])
except ImportError as e:
    print(f"Error importing flet: {e}")