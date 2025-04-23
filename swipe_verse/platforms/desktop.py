"""Desktop platform for SwipeVerse."""

import os
from pathlib import Path
from typing import Any, Dict, Union

from swipe_verse.main import run_app


def run_desktop_app(config: Dict[str, Any]) -> None:
    """Run the desktop application.
    
    Args:
        config: Application configuration
    """
    # Run the app in desktop mode
    run_app(platform="desktop", config=config)


def prepare_desktop_build(config: Dict[str, Any], output_dir: Union[str, Path]) -> Path:
    """Prepare files for desktop distribution.
    
    Args:
        config: Application configuration
        output_dir: Output directory for build files
        
    Returns:
        Path to the output directory
    """
    output_dir = Path(output_dir) / "swipe_verse_desktop"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Copy necessary files
    with open(output_dir / "launch.py", "w") as f:
        f.write("""#!/usr/bin/env python3
from swipe_verse.main import run_app
from swipe_verse.main import initialize_app

if __name__ == "__main__":
    config = initialize_app()
    run_app(platform="desktop", config=config)
""")
    
    # Make launch.py executable
    os.chmod(output_dir / "launch.py", 0o755)
    
    return output_dir