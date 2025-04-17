# ui/settings_screen.py
from typing import Any, Callable, Dict, Optional

import flet as ft


# Note: For Flet 0.27.x compatibility
# We're using a standard class instead of UserControl which is only in newer Flet versions
class SettingsScreen:
    def __init__(
        self,
        on_save: Callable[[Dict[str, Any]], None],
        on_cancel: Callable[[], Any],
        settings: Dict[str, Any],
    ):
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.settings = settings
        self.page: Optional[ft.Page] = None

        # Settings form controls
        self.player_name_field: Optional[ft.TextField] = None
        self.difficulty_dropdown: Optional[ft.Dropdown] = None
        self.filter_dropdown: Optional[ft.Dropdown] = None
        self.theme_dropdown: Optional[ft.Dropdown] = None

    def build(self) -> ft.Container:
        # Responsive design adjustments
        page_width = 800  # Default width
        if self.page and hasattr(self.page, "width") and self.page.width is not None:
            page_width = self.page.width

        is_mobile = page_width < 600
        padding_value = 20 if is_mobile else 40
        title_size = 24 if is_mobile else 32

        # Set form width based on page width
        form_width: float = 500
        if is_mobile:
            form_width = page_width * 0.9

        # Create form fields
        self.player_name_field = ft.TextField(
            label="Player Name",
            value=self.settings.get("player_name", "Player"),
            width=form_width,
            autofocus=True,
        )

        self.difficulty_dropdown = ft.Dropdown(
            label="Difficulty",
            width=form_width,
            options=[
                ft.dropdown.Option("easy", "Easy"),
                ft.dropdown.Option("standard", "Standard"),
                ft.dropdown.Option("hard", "Hard"),
            ],
            value=self.settings.get("difficulty", "standard"),
        )

        self.filter_dropdown = ft.Dropdown(
            label="Visual Filter",
            width=form_width,
            options=[
                ft.dropdown.Option("none", "None"),
                ft.dropdown.Option("pixelate", "Pixelate"),
                ft.dropdown.Option("cartoon", "Cartoon"),
                ft.dropdown.Option("posterize", "Posterize"),
                ft.dropdown.Option("blur", "Blur"),
                ft.dropdown.Option("grayscale", "Grayscale"),
            ],
            value=self.settings.get("filter", "none"),
        )

        self.theme_dropdown = ft.Dropdown(
            label="Game",
            width=form_width,
            options=[
                ft.dropdown.Option("kingdom", "Kingdom"),
                ft.dropdown.Option("business", "Corporate"),
            ],
            value=self.settings.get("game", "kingdom"),
        )

        # Create buttons
        save_button = ft.ElevatedButton(
            "Save", icon=ft.icons.SAVE, on_click=self._handle_save
        )

        cancel_button = ft.OutlinedButton(
            "Cancel", icon=ft.icons.CANCEL, on_click=lambda _: self.on_cancel()
        )

        # Create layout
        title = ft.Text(
            "Settings",
            size=title_size,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        content = ft.Column(
            controls=[
                title,
                ft.Container(height=20),  # Spacing
                self.player_name_field,
                ft.Container(height=10),  # Spacing
                self.difficulty_dropdown,
                ft.Container(height=10),  # Spacing
                self.theme_dropdown,
                ft.Container(height=10),  # Spacing
                self.filter_dropdown,
                ft.Container(height=20),  # Spacing
                ft.Row(
                    [cancel_button, save_button], alignment=ft.MainAxisAlignment.END
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Main container
        return ft.Container(
            content=content,
            alignment=ft.alignment.center,
            padding=padding_value,
            expand=True,
        )

    def _handle_save(self, e: ft.ControlEvent) -> None:
        """Handle saving the settings"""
        # Validate player name
        if (
            not self.player_name_field
            or not self.player_name_field.value
            or len(self.player_name_field.value.strip()) == 0
        ):
            if self.player_name_field:
                self.player_name_field.error_text = "Please enter a player name"
                self.player_name_field.update()
            return

        # Ensure required fields are available
        difficulty_dropdown = self.difficulty_dropdown
        filter_dropdown = self.filter_dropdown
        theme_dropdown = self.theme_dropdown
        if difficulty_dropdown is None or filter_dropdown is None or theme_dropdown is None:
            return

        # Collect settings, including selected game
        updated_settings = {
            "player_name": self.player_name_field.value.strip(),
            "difficulty": difficulty_dropdown.value,
            "filter": filter_dropdown.value,
        }
        # Include game/scenario selection
        updated_settings["game"] = theme_dropdown.value

        # Call save handler
        self.on_save(updated_settings)
