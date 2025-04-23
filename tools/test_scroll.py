#!/usr/bin/env python3
"""
Test script to list scroll-related attributes in Flet Row component.
"""
import sys
from pathlib import Path

# Add parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    import flet as ft
    scroll_attrs = [a for a in dir(ft.Row) if 'scroll' in a.lower()]
    print(f"Scroll-related attributes in ft.Row: {scroll_attrs}")
except ImportError as e:
    print(f"Failed to import flet: {e}")
