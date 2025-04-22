"""Android platform for SwipeVerse."""

import os
import shutil
from pathlib import Path
from swipe_verse.main import initialize_app


def prepare_android_build(config, output_dir):
    """Prepare files for Android build.
    
    Args:
        config: Application configuration
        output_dir: Output directory for build files
        
    Returns:
        Path to the output directory
    """
    output_dir = Path(output_dir) / "swipe_verse_android"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Create the app directory structure
    app_dir = output_dir / "app"
    app_dir.mkdir(exist_ok=True)
    
    assets_dir = app_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Copy asset files if available
    source_assets = Path(config.get("assets_dir", ""))
    if source_assets.exists() and source_assets.is_dir():
        # Create subdirectories
        (assets_dir / "default").mkdir(exist_ok=True, parents=True)
        (assets_dir / "default" / "card_fronts").mkdir(exist_ok=True)
        (assets_dir / "default" / "resource_icons").mkdir(exist_ok=True)
        (assets_dir / "themes").mkdir(exist_ok=True)
        
        # Copy assets recursively (would be implemented with shutil.copytree)
        print(f"Would copy assets from {source_assets} to {assets_dir}")
    
    # Create the main.py file
    with open(app_dir / "main.py", "w") as f:
        f.write(f"""import os
import flet as ft
from swipe_verse.main import run_app
from swipe_verse.main import initialize_app

# Set environment variables for packaged app
os.environ["SWIPEVERSE_ASSETS"] = "./assets"
os.environ["SWIPEVERSE_SCENARIOS"] = "./scenarios"

def main():
    # Initialize app with Android-specific settings
    config = initialize_app(
        game_theme="{config.get('game_theme', 'tutorial')}",
        debug={str(config.get('debug', False)).lower()}
    )
    
    # Run the app in Android mode
    run_app(platform="android", config=config)

if __name__ == "__main__":
    main()
""")
    
    # Create the app configuration for Flet
    with open(output_dir / "flet.json", "w") as f:
        f.write(f"""{{
    "name": "SwipeVerse",
    "version": "{config.get('version', '0.1.11')}",
    "description": "A card-based decision game",
    "module_name": "app.main",
    "module_function": "main",
    "app_dir": "app",
    "asset_dir": "app/assets",
    "persistent_storage": true
}}
""")
    
    # Create a README with build instructions
    with open(output_dir / "README.md", "w") as f:
        f.write("""# SwipeVerse for Android

This directory contains the files needed to build SwipeVerse for Android.

## Building the APK

1. Install the Flet CLI tools:
   ```
   pip install flet-cli
   ```

2. Build the APK:
   ```
   cd swipe_verse_android
   flet build apk
   ```

3. Install the APK on your Android device.

## Testing the build

You can test the build locally using:
```
flet run -d
```

This will run the app in development mode.
""")
    
    return output_dir