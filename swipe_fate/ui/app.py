from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union, Coroutine

import flet as ft

from swipe_fate.models.game_state import GameState
from swipe_fate.services.asset_manager import AssetManager
from swipe_fate.services.config_loader import ConfigLoader
from swipe_fate.services.game_logic import GameLogic
from swipe_fate.services.image_processor import ImageProcessor


# Note: For Flet 0.27.x compatibility
# We're using a standard class instead of UserControl which is only in newer Flet versions
class SwipeFateApp:
    def __init__(self, page: ft.Page, config_path: Optional[str] = None, assets_path: Optional[str] = None) -> None:
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
        self.current_screen: Optional[Any] = None
        self.loading: ft.ProgressRing
        self.is_mobile: bool = False

        # Configure the page
        self._configure_page()

    def _configure_page(self) -> None:
        """Configure the page settings"""
        self.page.title = "Swipe Fate"
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
        if self.current_screen and hasattr(self.current_screen, 'update'):
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
                Path(__file__).parent.parent / "config" / "default_game.json"
            )

        self.loading.visible = True
        self.page.update()

        try:
            config = await self.config_loader.load_config(config_path)
            self.game_state = GameState.new_game(config)
            if self.game_state:  # Extra safety check
                self.game_logic = GameLogic(self.game_state, config)

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

        # Preload card back
        await self.asset_manager.get_image(str(self.game_state.theme.card_back))

        # Preload resource icons
        for icon_path in self.game_state.theme.resource_icons.values():
            await self.asset_manager.get_image(str(icon_path))

    async def navigate_to(self, screen_name: str, **kwargs: Any) -> None:
        """Navigate to a specific screen"""
        # Import screens here to avoid circular imports
        from swipe_fate.ui.game_screen import GameScreen
        from swipe_fate.ui.settings_screen import SettingsScreen
        from swipe_fate.ui.title_screen import TitleScreen

        if screen_name == "title":
            self.current_screen = TitleScreen(
                on_start_game=lambda: self.page.run_async(self.navigate_to("game")),
                on_load_config=self._handle_load_config,
                on_settings=lambda: self.page.run_async(self.navigate_to("settings")),
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
                    Path(__file__).parent.parent / "config" / "default_game.json"
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
            self.current_screen = TitleScreen(
                on_start_game=lambda: self.page.run_async(self.navigate_to("game")),
                on_load_config=self._handle_load_config,
                on_settings=lambda: self.page.run_async(self.navigate_to("settings")),
            )

        # Update the UI
        self.page.controls.clear()
        self.page.controls.append(self.current_screen)
        self.page.update()

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
        if self.game_state:
            self.game_state.player_name = settings.get("player_name", "Player")
            self.game_state.difficulty = settings.get("difficulty", "standard")

            # Apply theme/filter changes if needed
            filter_type = settings.get("filter")
            if filter_type and filter_type != "none":
                # Update assets with the new filter
                pass

        self.page.run_async(self.navigate_to("title"))

    def _get_current_settings(self) -> dict:
        """Get current settings for the settings screen"""
        if not self.game_state:
            return {"player_name": "Player", "difficulty": "standard", "filter": "none"}

        return {
            "player_name": self.game_state.player_name,
            "difficulty": self.game_state.difficulty,
            "filter": "none",  # Currently active filter
        }

    def build(self) -> ft.Container:
        # Start with a placeholder that will be replaced when navigate_to is called
        self.current_screen = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(), ft.Text("Loading Swipe Fate...")],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.center,
        )

        # Schedule the navigation to happen after the initial render
        self.page.run_async(self.navigate_to("title"))

        # Container that fills the page
        return ft.Container(expand=True, content=self.current_screen)


def main(page: ft.Page) -> None:
    app = SwipeFateApp(page)
    page.add(app.build())
