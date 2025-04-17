from pathlib import Path
from typing import Any, Dict, Optional

import flet as ft

from swipe_verse.models.game_state import GameState
from swipe_verse.services.asset_manager import AssetManager
from swipe_verse.services.config_loader import ConfigLoader
from swipe_verse.services.game_logic import GameLogic
from swipe_verse.services.image_processor import ImageProcessor


# Note: For Flet 0.27.x compatibility
# We're using a standard class instead of UserControl which is only in newer Flet versions
class SwipeVerseApp:
    def __init__(
        self,
        page: ft.Page,
        config_path: Optional[str] = None,
        assets_path: Optional[str] = None,
    ) -> None:
        self.page = page
        self.config_path = config_path

        # Set up base paths
        package_dir = Path(__file__).parent.parent
        self.base_path = Path(assets_path) if assets_path else package_dir
        self.default_assets_path = package_dir / "assets" / "default"

        # Initialize services
        self.config_loader = ConfigLoader(base_path=str(self.base_path))
        self.asset_manager = AssetManager(
            base_path=str(self.base_path),
            default_assets_path=str(self.default_assets_path),
        )
        self.image_processor = ImageProcessor()

        # Game state
        self.game_state: Optional[GameState] = None
        self.game_logic: Optional[GameLogic] = None
        self.current_screen: Any = None
        self.loading: ft.ProgressRing
        self.is_mobile: bool = False
        self.current_filter: Optional[str] = None

        # Configure the page
        self._configure_page()

    def _configure_page(self) -> None:
        """Configure the page settings"""
        self.page.title = "Swipe Verse"
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 0
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.on_resize = self._handle_resize

        # Set up responsive design
        self.is_mobile = self.page.width is not None and self.page.width < 600
        self.page.on_window_event = self._handle_window_event

        # Add a loading indicator
        self.loading = ft.ProgressRing()
        self.loading.visible = False
        self.page.overlay.append(self.loading)

    def _handle_resize(self, e: ft.ControlEvent) -> None:
        """Handle page resize events"""
        # Update responsive layout flag
        self.is_mobile = self.page.width < 600 if self.page.width is not None else False

        # Update the current screen if it exists
        if self.current_screen and hasattr(self.current_screen, "update"):
            self.current_screen.update()

    def _handle_window_event(self, e: ft.ControlEvent) -> None:
        """Handle window events like focus/blur"""
        if e.data == "focus":
            # Could resume game, reload assets, etc.
            pass
        elif e.data == "blur":
            # Could pause game, save state, etc.
            pass

    async def load_config(self, config_path: Optional[str] = None) -> bool:
        """Load a game configuration"""
        if not config_path:
            config_path = self.config_path or str(
                Path(__file__).parent.parent / "config" / "kingdom_game.json"
            )

        self.loading.visible = True
        self.page.update()

        try:
            # Store the config path for theme detection
            self.config_path = config_path

            config = await self.config_loader.load_config(config_path)
            self.game_state = GameState.new_game(config)
            if self.game_state:  # Extra safety check
                self.game_logic = GameLogic(self.game_state, config)

                # Set current filter from game state if it exists
                if (
                    hasattr(self.game_state, "active_filter")
                    and self.game_state.active_filter
                ):
                    self.current_filter = self.game_state.active_filter

            # Preload assets in background
            await self._preload_assets()

            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error loading game: {str(e)}"), action="OK"
            )
            self.page.snack_bar.open = True
            self.page.update()
            return False
        finally:
            self.loading.visible = False
            self.page.update()

    async def _preload_assets(self) -> None:
        """Preload commonly used assets"""
        if not self.game_state:
            return

        # Preload card back with current filter if any
        await self.asset_manager.get_image(
            str(self.game_state.theme.card_back), filter_type=self.current_filter
        )

        # Preload resource icons with current filter if any
        for icon_path in self.game_state.theme.resource_icons.values():
            await self.asset_manager.get_image(
                str(icon_path), filter_type=self.current_filter
            )

    async def navigate_to(self, screen_name: str, **kwargs: Any) -> None:
        """Navigate to a specific screen"""
        # Import screens here to avoid circular imports
        from swipe_verse.ui.game_screen import GameScreen
        from swipe_verse.ui.settings_screen import SettingsScreen
        from swipe_verse.ui.title_screen import TitleScreen

        if screen_name == "title":
            # Get backstory from game_logic if it exists
            backstory = None
            if (
                self.game_logic
                and hasattr(self.game_logic, "config")
                and self.game_logic.config
            ):
                backstory = self.game_logic.config.game_info.backstory

            self.current_screen = TitleScreen(
                on_start_game=lambda: self.page.run_async(self.navigate_to("game")),
                on_load_config=self._handle_load_config,
                on_settings=lambda: self.page.run_async(self.navigate_to("settings")),
                backstory=backstory,
            )
        elif screen_name == "game":
            if not self.game_state:
                # Create a new game with default config if none exists
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Loading default game configuration..."),
                    action="OK",
                )
                self.page.snack_bar.open = True
                self.page.update()

                default_config_path = str(
                    Path(__file__).parent.parent / "config" / "kingdom_game.json"
                )
                success = await self.load_config(default_config_path)
                if not success:
                    await self.navigate_to("title")
                    return

            # Check to ensure game_state and game_logic are not None
            if self.game_state and self.game_logic:
                self.current_screen = GameScreen(
                    game_state=self.game_state,
                    game_logic=self.game_logic,
                    on_new_game=lambda: self.page.run_async(self.new_game()),
                    on_main_menu=lambda: self.page.run_async(self.navigate_to("title")),
                )
        elif screen_name == "settings":
            self.current_screen = SettingsScreen(
                on_save=self._handle_save_settings,
                on_cancel=lambda: self.page.run_async(self.navigate_to("title")),
                settings=self._get_current_settings(),
            )
        else:
            # Default to title screen
            # Get backstory if available
            backstory = None
            if (
                self.game_logic
                and hasattr(self.game_logic, "config")
                and self.game_logic.config
            ):
                backstory = self.game_logic.config.game_info.backstory

            self.current_screen = TitleScreen(
                on_start_game=lambda: self.page.run_async(self.navigate_to("game")),
                on_load_config=self._handle_load_config,
                on_settings=lambda: self.page.run_async(self.navigate_to("settings")),
                backstory=backstory,
            )

        # Update the UI
        self.page.controls.clear()
        self.page.controls.append(self.current_screen)
        self.page.update()

        # Call did_mount for components that need initialization
        if screen_name == "title" and hasattr(self.current_screen, "did_mount"):
            # Support sync or async did_mount
            import inspect

            result = self.current_screen.did_mount()
            if inspect.isawaitable(result):
                await result

    async def _handle_load_config(self, config_path: str) -> None:
        """Handle loading a new configuration"""
        success = await self.load_config(config_path)
        if success:
            await self.navigate_to("game")

    async def new_game(self) -> None:
        """Start a new game with the current settings"""
        # Reset game state with the same configuration
        if self.game_state and self.game_logic:
            config = self.game_logic.config
            player_name = self.game_state.player_name
            difficulty = self.game_state.difficulty
            self.game_state = GameState.new_game(
                config, player_name=player_name, difficulty=difficulty
            )
            if self.game_state:  # Safety check
                self.game_logic = GameLogic(self.game_state, config)
                await self.navigate_to("game")

    def _handle_save_settings(self, settings: Dict[str, Any]) -> None:
        """Handle saving settings"""
        # Get player name and difficulty
        player_name = settings.get("player_name", "Player")
        difficulty = settings.get("difficulty", "standard")

        # Check if game scenario changed
        selected_game = settings.get("game", "kingdom")
        game_changed = False

        if hasattr(self, "config_path") and self.config_path:
            current_game = "kingdom"
            if "business" in self.config_path:
                current_game = "business"
            elif "kingdom" in self.config_path:
                current_game = "kingdom"

            if current_game != selected_game:
                game_changed = True

        # Apply theme change if needed
        if game_changed or not self.game_state:
            # Determine the new config path based on selected theme
            config_dir = Path(__file__).parent.parent / "config"
            new_config_path = str(config_dir / f"{selected_game}_game.json")

            # Save the settings temporarily
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Switching to {selected_game.capitalize()} game..."),
                action="OK",
            )
            self.page.snack_bar.open = True
            self.page.update()

            # Schedule loading the new config
            self.page.run_async(
                self._load_and_switch_theme(new_config_path, player_name, difficulty)
            )
        else:
            # Just update existing game state
            if self.game_state:
                self.game_state.player_name = player_name
                self.game_state.difficulty = difficulty

                # Apply filter changes if needed
                filter_type = settings.get("filter")
                if filter_type and filter_type != "none":
                    # Store the selected filter in both app and game state
                    self.current_filter = filter_type
                    self.game_state.active_filter = filter_type

                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Applying {filter_type} filter..."),
                        action="OK",
                    )
                    self.page.snack_bar.open = True
                    self.page.update()

                else:
                    # Reset filter if none selected
                    self.current_filter = None
                    self.game_state.active_filter = None

            # Return to title screen
            self.page.run_async(self.navigate_to("title"))

    async def _load_and_switch_theme(
        self, config_path: str, player_name: str, difficulty: str
    ) -> None:
        """Load a new configuration with the selected theme"""
        success = await self.load_config(config_path)
        if success and self.game_state:
            # Update player settings
            self.game_state.player_name = player_name
            self.game_state.difficulty = difficulty

        # Navigate back to title screen
        await self.navigate_to("title")

    def _get_current_settings(self) -> dict:
        """Get current settings for the settings screen"""
        if not self.game_state:
            return {
                "player_name": "Player",
                "difficulty": "standard",
                "filter": self.current_filter or "none",
                "game": "kingdom",
            }

        # Determine current game scenario by inspecting the config path
        current_game = "kingdom"  # Default
        if hasattr(self, "config_path") and self.config_path:
            if "business" in self.config_path:
                current_game = "business"
            elif "kingdom" in self.config_path:
                current_game = "kingdom"

        return {
            "player_name": self.game_state.player_name,
            "difficulty": self.game_state.difficulty,
            "filter": self.current_filter or "none",
            "game": current_game,
        }

    def build(self) -> ft.Container:
        # Start with a placeholder that will be replaced when navigate_to is called
        self.current_screen = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(), ft.Text("Loading Swipe Verse...")],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.center,
        )

        # Schedule the navigation to happen after the initial render
        # This will trigger game selector initialization because it calls did_mount
        self.page.run_async(self.navigate_to("title"))

        # Container that fills the page
        return ft.Container(expand=True, content=self.current_screen)


def main(page: ft.Page) -> None:
    app = SwipeVerseApp(page)
    page.add(app.build())
