#!/usr/bin/env python
"""
SwipeFate - A card-based decision game with swipe mechanics
"""
import flet as ft
import sys
import os
from argparse import ArgumentParser

# Add project root to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse_args():
    """Parse command line arguments"""
    parser = ArgumentParser(description="Run SwipeFate card decision game")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Import after argument parsing
    from new_src.swipe_fate.main import main
    
    print(f"Starting SwipeFate on {args.host}:{args.port}")
    ft.app(target=main, host=args.host, port=args.port, view=ft.AppView.WEB_BROWSER)