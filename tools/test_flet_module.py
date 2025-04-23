#!/usr/bin/env python3
"""
Test script to check Flet installation and environment.
"""
import sys
from pathlib import Path

# Add parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"sys.path: {sys.path}")

try:
    import flet
    print(f"Flet version: {flet.__version__ if hasattr(flet, '__version__') else 'unknown'}")
    print(f"Flet path: {flet.__file__}")
    print(f"Flet dir: {[attr for attr in dir(flet) if not attr.startswith('_')]}")
except ImportError as e:
    print(f"Failed to import flet: {e}")