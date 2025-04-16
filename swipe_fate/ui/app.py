# ui/app.py
import flet as ft
from reigns_game.models.game_state import GameState
from reigns_game.services.game_logic import GameLogic
from reigns_game.services.config_loader import ConfigLoader
from reigns_game.services.asset_manager import AssetManager
from reigns_game.ui.title_screen import TitleScreen
from reigns_game.ui.game_screen import GameScreen
from reigns_game.ui.settings_screen import SettingsScreen


class ReignsApp(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.config_loader = ConfigLoader()
        self.asset_manager = AssetManager(
            base_path=".",
            default_assets_path="./reigns_game/assets/default"
        )
        self.game_state = None
        self.game_logic = None
        self.current_screen = None
        
        # Configure the page
        self._configure_page()
    
    def _configure_page(self):
        """Configure the page settings"""
        self.page.title = "Reigns Game"
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
    
    def _handle_resize(self, e):
        """Handle page resize events"""
        # Update responsive layout flag
        self.is_mobile = self.page.width < 600
        
        # Update the current screen if it exists
        if self.current_screen:
            self.current_screen.update()
    
    def _handle_window_event(self, e):
        """Handle window events like focus/blur"""
        if e.data == "focus":
            # Could resume game, reload assets, etc.
            pass
        elif e.data == "blur":
            # Could pause game, save state, etc.
            pass
    
    async def load_config(self, config_path: str):
        """Load a game configuration"""
        self.loading.visible = True
        self.page.update()
        
        try:
            config = await self.config_loader.load_config(config_path)
            self.game_state = GameState.new_game(config)
            self.game_logic = GameLogic(self.game_state, config)
            
            # Preload assets in background
            await self._preload_assets()
            
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error loading game: {str(e)}"),
                action="OK"
            )
            self.page.snack_bar.open = True
            self.page.update()
            return False
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def _preload_assets(self):
        """Preload commonly used assets"""
        if not self.game_state:
            return
            
        # Preload card back
        await self.asset_manager.get_image(self.game_state.theme.card_back)
        
        # Preload resource icons
        for icon_path in self.game_state.theme.resource_icons.values():
            await self.asset_manager.get_image(icon_path)
    
    def navigate_to(self, screen_name: str, **kwargs):
        """Navigate to a specific screen"""
        if screen_name == "title":
            self.current_screen = TitleScreen(
                on_start_game=lambda: self.navigate_to("game"),
                on_load_config=self._handle_load_config,
                on_settings=lambda: self.navigate_to("settings")
            )
        elif screen_name == "game":
            if not self.game_state:
                # Create a new game with default config if none exists
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Loading default game configuration..."),
                    action="OK"
                )
                self.page.snack_bar.open = True
                self.page.update()
                
                default_config_path = "./reigns_game/config/default_game.json"
                success = await self.load_config(default_config_path)
                if not success:
                    self.navigate_to("title")
                    return
            
            self.current_screen = GameScreen(
                game_state=self.game_state,
                game_logic=self.game_logic
            )
        elif screen_name == "settings":
            self.current_screen = SettingsScreen(
                on_save=self._handle_save_settings,
                on_cancel=lambda: self.navigate_to("title"),
                settings=self._get_current_settings()
            )
        else:
            # Default to title screen
            self.current_screen = TitleScreen(
                on_start_game=lambda: self.navigate_to("game"),
                on_load_config=self._handle_load_config,
                on_settings=lambda: self.navigate_to("settings")
            )
        
        # Update the UI
        self.page.controls.clear()
        self.page.controls.append(self.current_screen)
        self.page.update()
    
    async def _handle_load_config(self, config_path: str):
        """Handle loading a new configuration"""
        success = await self.load_config(config_path)
        if success:
            self.navigate_to("game")
    
    def _handle_save_settings(self, settings: dict):
        """Handle saving settings"""
        if self.game_state:
            self.game_state.player_name = settings.get("player_name", "Player")
            self.game_state.difficulty = settings.get("difficulty", "standard")
            
            # Apply theme/filter changes if needed
            filter_type = settings.get("filter")
            if filter_type and filter_type != "none":
                # Update assets with the new filter
                pass
        
        self.navigate_to("title")
    
    def _get_current_settings(self) -> dict:
        """Get current settings for the settings screen"""
        if not self.game_state:
            return {
                "player_name": "Player",
                "difficulty": "standard",
                "filter": "none"
            }
        
        return {
            "player_name": self.game_state.player_name,
            "difficulty": self.game_state.difficulty,
            "filter": "none"  # Currently active filter
        }
    
    def build(self):
        # Start with the title screen
        self.navigate_to("title")
        
        # Container that fills the page
        return ft.Container(
            expand=True,
            content=self.current_screen
        )


def main(page: ft.Page):
    app = ReignsApp(page)
    page.add(app)