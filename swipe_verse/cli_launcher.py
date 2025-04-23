#!/usr/bin/env python
"""Cross-platform launcher for SwipeVerse."""

import os
import sys
import platform
import subprocess
import importlib.util
from pathlib import Path
import argparse


def launch_platform(
    target_platform: str = None,
    game: str = None,
    debug: bool = False,
    port: int = 8550,
    host: str = "127.0.0.1",
    build_dir: Path = None
) -> None:
    """Launch the application on the specified platform.
    
    Args:
        target_platform: Target platform to launch on (android, web, desktop, ios)
        game: Game theme to load
        debug: Enable debug mode
        port: Port to use for web server (web mode only)
        host: Host address to bind to (web mode only, e.g., '0.0.0.0' for all interfaces)
        build_dir: Directory to output build files (optional)
    """
    # Get the SwipeVerse package directory
    package_dir = Path(__file__).parent
    
    # Initialize app configuration
    from swipe_verse.main import initialize_app
    
    config = initialize_app(
        game_theme=game,
        debug=debug
    )
    
    # Add port and host to config for web
    if target_platform == "web":
        config["port"] = port
        config["host"] = host
    
    # Output directory for builds
    if build_dir is None:
        build_dir = os.getcwd()
    
    # Launch based on platform
    if target_platform == "android":
        try:
            # Import Android platform module
            from swipe_verse.platforms import android
            
            print("Preparing Android build...")
            output_dir = android.prepare_android_build(config, build_dir)
            
            print(f"\nAndroid build prepared in: {output_dir}")
            print("\nTo build the APK, install flet command-line tools and run:")
            print(f"cd {output_dir} && flet build apk")
            
        except ImportError:
            print("Error: Android platform module not available.")
            print("Make sure to install with: pip install swipe-verse[android]")
        
    elif target_platform == "ios":
        # For iOS, we'd need macOS
        if platform.system() != "Darwin":
            print("iOS builds can only be created on macOS.")
            return
        
        # iOS implementation would be similar to Android
        print("iOS platform support is coming soon.")
        print("It will require macOS for building.")
        
    elif target_platform == "web":
        try:
            # Import Web platform module
            from swipe_verse.platforms import web
            
            if build_dir:
                # Prepare web build files
                print("Preparing web build...")
                output_dir = web.prepare_web_build(config, build_dir)
                
                print(f"\nWeb build prepared in: {output_dir}")
                print(f"To run the web version, execute: python {output_dir}/launch.py")
            else:
                # Run web server directly
                print(f"Launching SwipeVerse web server on port {port}...")
                web.run_web_server(config)
                
        except ImportError:
            print("Error: Web platform module not available.")
            print("Make sure to install with: pip install swipe-verse[web]")
            
            # Fallback to basic execution
            from swipe_verse.main import run_app
            run_app(platform="web", config=config, port=port, host=host)
        
    else:  # Default to desktop
        try:
            # Import Desktop platform module
            from swipe_verse.platforms import desktop
            
            if build_dir and build_dir != os.getcwd():
                # Prepare desktop build files
                print("Preparing desktop build...")
                output_dir = desktop.prepare_desktop_build(config, build_dir)
                
                print(f"\nDesktop build prepared in: {output_dir}")
            else:
                # Run desktop app directly
                print("Launching SwipeVerse desktop app...")
                desktop.run_desktop_app(config)
                
        except ImportError:
            print("Error: Desktop platform module not available.")
            print("Falling back to basic execution...")
            
            # Fallback to basic execution
            from swipe_verse.main import run_app
            run_app(platform="desktop", config=config)


def main() -> None:
    """Command-line entry point for the launcher."""
    parser = argparse.ArgumentParser(description="SwipeVerse Platform Launcher")
    parser.add_argument(
        "--platform", 
        choices=["desktop", "web", "android", "ios"],
        default="desktop",
        help="Platform to launch on"
    )
    parser.add_argument(
        "--game", 
        help="Game theme to load (tutorial, kingdom, business)",
        default="tutorial"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=8550,
        help="Port to use for web server (web mode only)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind to (web mode only, e.g., '0.0.0.0' for all interfaces)"
    )
    parser.add_argument(
        "--build-dir",
        help="Directory to output build files",
        type=Path,
        default=None
    )
    
    args = parser.parse_args()
    launch_platform(
        target_platform=args.platform, 
        game=args.game, 
        debug=args.debug,
        port=args.port,
        host=args.host,
        build_dir=args.build_dir
    )


if __name__ == "__main__":
    main()