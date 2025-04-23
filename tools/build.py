#!/usr/bin/env python
"""Build script for SwipeVerse.

This script helps package SwipeVerse for different platforms.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path to ensure imports work when called from tools directory
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def build_distribution():
    """Build Python distribution packages (wheel and sdist)."""
    # Ensure build module is installed
    try:
        # Just check if the module is available
        import importlib.util
        if importlib.util.find_spec("build") is None:
            raise ImportError("build module not found")
    except ImportError:
        print("Installing build module...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "build"])
    
    # Change to project root directory
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)
    
    print(f"Building distribution packages in {project_root}...")
    subprocess.check_call([sys.executable, "-m", "build"])
    
    print("\nPackages built in ./dist/")

def build_platform(platform, game, debug, build_dir):
    """Build for a specific platform using the platform launcher."""
    # Import the launcher module
    from swipe_verse.cli_launcher import launch_platform
    
    # Change to project root directory
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)
    
    if not build_dir:
        build_dir = project_root / "dist" / platform
        os.makedirs(build_dir, exist_ok=True)
    
    print(f"Building for platform: {platform}")
    print(f"Output directory: {build_dir}")
    
    # Launch the platform-specific build process
    launch_platform(
        target_platform=platform,
        game=game,
        debug=debug,
        build_dir=build_dir
    )

def main():
    """Parse arguments and execute build commands."""
    parser = argparse.ArgumentParser(
        description="SwipeVerse build tool for packaging and distribution"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Build command")
    
    # Distribution package build command
    subparsers.add_parser(
        "dist", help="Build Python distribution packages"
    )
    
    # Platform-specific build command
    platform_parser = subparsers.add_parser(
        "platform", help="Build for a specific platform"
    )
    platform_parser.add_argument(
        "--platform",
        choices=["desktop", "web", "android", "ios"],
        required=True,
        help="Platform to build for"
    )
    platform_parser.add_argument(
        "--game",
        default="tutorial",
        help="Game theme to include in the build"
    )
    platform_parser.add_argument(
        "--debug",
        action="store_true",
        help="Include debug information in the build"
    )
    platform_parser.add_argument(
        "--build-dir",
        type=Path,
        help="Directory to output build files"
    )
    
    args = parser.parse_args()
    
    if args.command == "dist":
        build_distribution()
    elif args.command == "platform":
        build_platform(
            args.platform,
            args.game,
            args.debug,
            args.build_dir
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()