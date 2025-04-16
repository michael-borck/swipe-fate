import argparse
import sys

import flet as ft


def main():
    """Entry point for the Swipe Verse game application."""
    parser = argparse.ArgumentParser(description="Swipe Verse - A multiverse card-based decision game")
    parser.add_argument("--config", type=str, help="Path to game configuration file")
    parser.add_argument(
        "--mode",
        choices=["ui", "tui", "cli"],
        default="ui",
        help="Game interface mode: UI (graphical), TUI (terminal), CLI (command line)",
    )
    parser.add_argument(
        "--theme",
        choices=["kingdom", "business", "science", "space", "tutorial"],
        default="kingdom",
        help="Game theme to launch with",
    )
    parser.add_argument("--assets", type=str, help="Path to custom assets directory")
    parser.add_argument("--port", type=int, default=0, help="Port number for web view (0 = auto)")

    args = parser.parse_args()

    # Import the appropriate app based on the mode
    if args.mode == "ui":
        # Use the Flet UI
        from swipe_verse.ui.app import SwipeVerseApp

        def launch_ui(page: ft.Page):
            # Initialize settings
            # If config is not specified but theme is, use the theme config
            config_path = args.config
            if not config_path and args.theme:
                from pathlib import Path
                config_dir = Path(__file__).parent / "config"
                config_path = str(config_dir / f"{args.theme}_game.json")
            
            assets_path = args.assets if args.assets else None

            # Create and add the app to the page
            app = SwipeVerseApp(page=page, config_path=config_path, assets_path=assets_path)
            page.add(app)

        # Launch the app with Flet
        ft.app(target=launch_ui, port=args.port)

    elif args.mode == "tui":
        # Use the Terminal UI
        from swipe_verse.tui.tui_app import run_tui

        # If config is not specified but theme is, use the theme config
        config_path = args.config
        if not config_path and args.theme:
            from pathlib import Path
            config_dir = Path(__file__).parent / "config"
            config_path = str(config_dir / f"{args.theme}_game.json")
            
        assets_path = args.assets if args.assets else None
        run_tui(config_path, assets_path)

    elif args.mode == "cli":
        # Use the Command Line Interface
        from swipe_verse.cli.cli_app import run_cli

        # If config is not specified but theme is, use the theme config
        config_path = args.config
        if not config_path and args.theme:
            from pathlib import Path
            config_dir = Path(__file__).parent / "config"
            config_path = str(config_dir / f"{args.theme}_game.json")
            
        assets_path = args.assets if args.assets else None
        run_cli(config_path, assets_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
