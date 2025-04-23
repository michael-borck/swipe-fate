#!/usr/bin/env python3
"""
Test script to examine Flet component properties.
"""
import sys
from pathlib import Path

# Add parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    import flet as ft
    r = ft.Row([], scroll=ft.ScrollMode.AUTO)
    print("Row properties:")
    print(r.__dict__)
except ImportError as e:
    print(f"Failed to import flet: {e}")
