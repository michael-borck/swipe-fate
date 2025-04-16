# ui/settings_screen.py
import flet as ft
from typing import Callable, Dict, Any


class SettingsScreen(ft.UserControl):
    def __init__(
        self,
        on_save: Callable[[Dict[str, Any]], None],
        on_cancel: Callable,
        settings: Dict[str, Any]
    ):
        super().__init__()
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.settings = settings
        
        # Settings form controls
        self.player_name_field = None
        self.difficulty_dropdown = None
        self.filter_dropdown = None
    
    def build(self):
        # Responsive design adjustments
        is_mobile = self.page.width < 600 if self.page and self.page.width else True
        padding_value = 20 if is_mobile else 40
        title_size = 24 if is_mobile else 32
        form_width = self.page.width * 0.9 if is_mobile else 500
        
        # Create form fields
        self.player_name_field = ft.TextField(
            label="Player Name",
            value=self.settings.get("player_name", "Player"),
            width=form_width,
            autofocus=True
        )
        
        self.difficulty_dropdown = ft.Dropdown(
            label="Difficulty",
            width=form_width,
            options=[
                ft.dropdown.Option("easy", "Easy"),
                ft.dropdown.Option("standard", "Standard"),
                ft.dropdown.Option("hard", "Hard")
            ],
            value=self.settings.get("difficulty", "standard")
        )
        
        self.filter_dropdown = ft.Dropdown(
            label="Visual Filter",
            width=form_width,
            options=[
                ft.dropdown.Option("none", "None"),
                ft.dropdown.Option("grayscale", "Grayscale"),
                ft.dropdown.Option("cartoon", "Cartoon"),
                ft.dropdown.Option("oil_painting", "Oil Painting")
            ],
            value=self.settings.get("filter", "none")
        )
        
        # Create buttons
        save_button = ft.ElevatedButton(
            "Save",
            icon=ft.icons.SAVE,
            on_click=self._handle_save
        )
        
        cancel_button = ft.OutlinedButton(
            "Cancel",
            icon=ft.icons.CANCEL,
            on_click=lambda _: self.on_cancel()
        )
        
        # Create layout
        title = ft.Text(
            "Settings",
            size=title_size,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        content = ft.Column(
            controls=[
                title,
                ft.Container(height=20),  # Spacing
                self.player_name_field,
                ft.Container(height=10),  # Spacing
                self.difficulty_dropdown,
                ft.Container(height=10),  # Spacing
                self.filter_dropdown,
                ft.Container(height=20),  # Spacing
                ft.Row(
                    [cancel_button, save_button],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        # Main container
        return ft.Container(
            content=content,
            alignment=ft.alignment.center,
            padding=padding_value,
            expand=True
        )
    
    def _handle_save(self, e):
        """Handle saving the settings"""
        # Validate player name
        if not self.player_name_field.value or len(self.player_name_field.value.strip()) == 0:
            self.player_name_field.error_text = "Please enter a player name"
            self.player_name_field.update()
            return
        
        # Collect settings
        updated_settings = {
            "player_name": self.player_name_field.value.strip(),
            "difficulty": self.difficulty_dropdown.value,
            "filter": self.filter_dropdown.value
        }
        
        # Call save handler
        self.on_save(updated_settings)