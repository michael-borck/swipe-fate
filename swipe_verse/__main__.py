#!/usr/bin/env python
"""Main entry point for SwipeVerse."""

import argparse
import sys
from pathlib import Path

from swipe_verse.main import initialize_app, run_app


def main() -> None:
    """Parse arguments and launch the application."""
    parser = argparse.ArgumentParser(description="SwipeVerse - A card-based decision game")
    parser.add_argument(
        "--game", 
        help="Game theme to load (tutorial, kingdom, business)", 
        default="tutorial"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        help="Port to run web server on (web mode only)", 
        default=8550
    )
    parser.add_argument(
        "--host", 
        help="Host address to bind to (web mode only, e.g., '0.0.0.0' for all interfaces)", 
        default="127.0.0.1"
    )
    parser.add_argument(
        "--platform", 
        choices=["desktop", "web", "android", "ios"], 
        help="Platform to run on", 
        default="desktop"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    parser.add_argument(
        "--assets", 
        help="Custom assets directory", 
        type=Path, 
        default=None
    )
    
    args = parser.parse_args()
    
    # Initialize app configuration and game state
    app_config = initialize_app(
        game_theme=args.game,
        debug=args.debug,
        assets_dir=args.assets
    )
    
    # Run on the selected platform
    run_app(
        platform=args.platform, 
        config=app_config, 
        port=args.port,
        host=args.host
    )


if __name__ == "__main__":
    main()