#!/usr/bin/env python3
"""
Wrapper script to run SwipeFate directly from the repository
"""
import sys
import os
import argparse

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import flet as ft
from swipe_fate.main import main

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run SwipeFate application")
    parser.add_argument("--web", action="store_true", help="Run as web application")
    parser.add_argument("--port", type=int, default=8080, help="Port to run web server on (default: 8080)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the web server to (default: 127.0.0.1)")
    
    args, unknown = parser.parse_known_args()
    
    # Pass remaining args to flet
    sys.argv = [sys.argv[0]] + unknown
    
    # Run the app with web flag if specified
    if args.web:
        ft.app(
            target=main,
            view=ft.AppView.WEB_BROWSER,
            port=args.port,
            host=args.host
        )
    else:
        ft.app(target=main)