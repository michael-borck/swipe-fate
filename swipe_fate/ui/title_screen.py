# ui/title_screen.py
import flet as ft
from typing import Callable


class TitleScreen(ft.UserControl):
    def __init__(
        self,
        on_start_game: Callable,
        on_load_config: Callable[[str], None],
        on_settings: Callable
    ):
        super().__init__()
        self.on_start_game = on_start_game
        self.on_load_config = on_load_config
        self.on_settings = on_settings
    
    def build(self):
        # Responsive design adjustments
        is_mobile = self.page.width < 600 if self.page and self.page.width else True
        padding_value = 20 if is_mobile else 40
        title_size = 32 if is_mobile else 48
        button_width = 200 if is_mobile else 300
        
        # Title and logo
        title = ft.Text(
            "REIGNS",
            size=title_size,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )
        
        subtitle = ft.Text(
            "Make choices. Rule wisely.",
            size=16,
            italic=True,
            color=ft.colors.WHITE70,
            text_align=ft.TextAlign.CENTER,
        )
        
        # Main menu buttons
        start_button = ft.ElevatedButton(
            content=ft.Text("New Game", size=18),
            width=button_width,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_700,
            ),
            on_click=lambda _: self.on_start_game()
        )
        
        load_button = ft.ElevatedButton(
            content=ft.Text("Load Game", size=18),
            width=button_width,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_500,
            ),
            on_click=self._show_load_dialog
        )
        
        settings_button = ft.ElevatedButton(
            content=ft.Text("Settings", size=18),
            width=button_width,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_300,
            ),
            on_click=lambda _: self.on_settings()
        )
        
        # Layout for mobile
        content = ft.Column(
            controls=[
                ft.Container(height=40),  # Top spacing
                title,
                subtitle,
                ft.Container(height=40),  # Spacing
                start_button,
                ft.Container(height=20),  # Button spacing
                load_button,
                ft.Container(height=20),  # Button spacing
                settings_button,
                ft.Container(height=40),  # Bottom spacing
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Main container with background
        return ft.Container(
            content=content,
            expand=True,
            alignment=ft.alignment.center,
            padding=padding_value,
            decoration=ft.BoxDecoration(
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.colors.BLUE_900, ft.colors.INDIGO_900],
                )
            )
        )
    
    def _show_load_dialog(self, e):
        """Show dialog to load a configuration file"""
        # Create text field for file path or URL
        config_path_field = ft.TextField(
            label="Configuration file path or URL",
            hint_text="Enter file path or URL",
            width=400,
        )
        
        def close_dialog(load: bool = False):
            # Close the dialog
            self.page.dialog.open = False
            self.page.update()
            
            # If load button was clicked, call the load handler
            if load and config_path_field.value:
                self.on_load_config(config_path_field.value)
        
        # Create the dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Load Game Configuration"),
            content=ft.Column([
                ft.Text("Enter a file path or URL to a game configuration file:"),
                config_path_field,
                ft.Row([
                    ft.FilePicker(
                        on_result=self._handle_file_picker_result
                    )
                ])
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: close_dialog(False)),
                ft.TextButton("Load", on_click=lambda _: close_dialog(True))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # File picker for browsing local files
        def open_file_picker(_):
            self.page.overlay[0].pick_files(
                dialog_title="Select Game Configuration",
                allowed_extensions=["json"],
                file_type=ft.FilePickerFileType.CUSTOM
            )
        
        # Add the browse button
        browse_button = ft.ElevatedButton(
            "Browse Files",
            icon=ft.icons.FOLDER_OPEN,
            on_click=open_file_picker
        )
        
        dialog.content.controls.append(browse_button)
        
        # Register the file picker
        if not self.page.overlay:
            self.page.overlay.append(ft.FilePicker(
                on_result=self._handle_file_picker_result
            ))
        
        # Show the dialog
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()
    
    def _handle_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle the file picker result"""
        if e.files and len(e.files) > 0:
            # Get the selected file path
            file_path = e.files[0].path
            
            # Update the text field in the dialog
            if self.page.dialog and hasattr(self.page.dialog, "content"):
                for control in self.page.dialog.content.controls:
                    if isinstance(control, ft.TextField):
                        control.value = file_path
                        break
                
                self.page.dialog.update()