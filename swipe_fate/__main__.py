import argparse
import sys

import flet as ft


def main():
    """Entry point for the Swipe Fate game application."""
    parser = argparse.ArgumentParser(description="Swipe Fate - A card-based decision game")
    parser.add_argument("--config", type=str, help="Path to game configuration file")
    parser.add_argument(
        "--mode",
        choices=["ui", "tui", "cli"],
        default="ui",
        help="Game interface mode: UI (graphical), TUI (terminal), CLI (command line)",
    )
    parser.add_argument("--assets", type=str, help="Path to custom assets directory")
    parser.add_argument("--port", type=int, default=0, help="Port number for web view (0 = auto)")

    args = parser.parse_args()

    # Import the appropriate app based on the mode
    if args.mode == "ui":
        # Use the Flet UI
        from swipe_fate.ui.app import SwipeFateApp

        def launch_ui(page: ft.Page):
            # Initialize settings
            config_path = args.config if args.config else None
            assets_path = args.assets if args.assets else None

            # Create and add the app to the page
            app = SwipeFateApp(page=page, config_path=config_path, assets_path=assets_path)
            page.add(app)

        # Launch the app with Flet
        ft.app(target=launch_ui, port=args.port)

    elif args.mode == "tui":
        # Use the Terminal UI
        from swipe_fate.tui.tui_app import run_tui

        config_path = args.config if args.config else None
        assets_path = args.assets if args.assets else None
        run_tui(config_path, assets_path)

    elif args.mode == "cli":
        # Use the Command Line Interface
        from swipe_fate.cli.cli_app import run_cli

        config_path = args.config if args.config else None
        assets_path = args.assets if args.assets else None
        run_cli(config_path, assets_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
