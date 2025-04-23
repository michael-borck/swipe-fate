"""Web platform for SwipeVerse."""

import os
from pathlib import Path
from typing import Any, Dict, Union

from swipe_verse.main import run_app


def run_web_server(config: Dict[str, Any]) -> None:
    """Run the web server.
    
    Args:
        config: Application configuration
    """
    # Extract web-specific settings
    port = config.get("port", 8550)
    host = config.get("host", "127.0.0.1")
    
    # Run the app in web mode
    run_app(platform="web", config=config, port=port, host=host)


def prepare_web_build(config: Dict[str, Any], output_dir: Union[str, Path]) -> Path:
    """Prepare files for web distribution.
    
    Args:
        config: Application configuration
        output_dir: Output directory for build files
        
    Returns:
        Path to the output directory
    """
    output_dir = Path(output_dir) / "swipe_verse_web"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Extract web-specific settings
    port = config.get("port", 8550)
    host = config.get("host", "127.0.0.1")
    
    # Copy necessary files
    with open(output_dir / "launch.py", "w") as f:
        f.write(f"""#!/usr/bin/env python3
from swipe_verse.main import run_app
from swipe_verse.main import initialize_app

if __name__ == "__main__":
    # Initialize with web-specific settings
    config = initialize_app(game_theme="{config.get('game_theme', 'tutorial')}")
    run_app(platform="web", config=config, port={port}, host="{host}")
""")
    
    # Create a basic README with instructions
    with open(output_dir / "README.md", "w") as f:
        f.write(f"""# SwipeVerse Web

This is a web build of SwipeVerse.

## Running the Web Server

1. Make sure swipe-verse package is installed:
   ```
   pip install swipe-verse
   ```

2. Run the web server:
   ```
   python launch.py
   ```

3. Open your browser and navigate to:
   http://{host}:{port}/

## Configuration

To change the port or host, edit the launch.py file.
""")
    
    # Make launch.py executable
    os.chmod(output_dir / "launch.py", 0o755)
    
    return output_dir