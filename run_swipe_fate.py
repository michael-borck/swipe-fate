#!/usr/bin/env python3
"""
Wrapper script to run SwipeFate directly from the repository
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import flet as ft
from swipe_fate.main import main

if __name__ == "__main__":
    # Check for "--web" flag
    web_flag = "--web" in sys.argv
    
    # Remove our flag if present so it doesn't confuse the flet module
    if web_flag and "--web" in sys.argv:
        sys.argv.remove("--web")
    
    # Run the app with web flag if specified
    if web_flag:
        ft.app(target=main, view=ft.AppView.WEB_BROWSER)
    else:
        ft.app(target=main)