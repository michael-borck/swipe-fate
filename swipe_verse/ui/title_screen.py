from typing import Any, Callable, Coroutine, Optional, Union

import flet as ft

from swipe_verse.ui.components.game_selector import GameSelector


# Note: For Flet 0.27.x compatibility
# We're using a standard class instead of UserControl which is only in newer Flet versions
class TitleScreen:
    def __init__(
        self,
        on_start_game: Callable[[], Any],
        on_load_config: Union[
            Callable[[str], None], Callable[[str], Coroutine[Any, Any, Any]]
        ],
        on_settings: Callable[[], Any],
        backstory: Optional[str] = None,
    ) -> None:
        self.on_start_game = on_start_game
        self.on_load_config = on_load_config
        self.on_settings = on_settings
        self.backstory = backstory
        self.page: Optional[ft.Page] = None
        self.game_selector: Optional[GameSelector] = None

    async def did_mount(self):
        """Called when the component is added to the page"""
        if self.game_selector and self.page:
            await self.game_selector.load_games(self.page)

    def build(self) -> ft.Container:
        # Responsive design adjustments
        page_width = 800  # Default width
        if self.page and hasattr(self.page, "width") and self.page.width is not None:
            page_width = self.page.width

        is_mobile = page_width < 600
        padding_value = 20 if is_mobile else 40
        title_size = 32 if is_mobile else 48
        button_width = 200 if is_mobile else 300

        # Title and logo
        title = ft.Text(
            "SWIPE VERSE",
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
        ft.ElevatedButton(
            content=ft.Text("New Game", size=18),
            width=button_width,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_700,
            ),
            on_click=lambda _: self.on_start_game(),
        )

        ft.ElevatedButton(
            content=ft.Text("Load Game", size=18),
            width=button_width,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_500,
            ),
            on_click=self._show_load_dialog,
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
            on_click=lambda _: self.on_settings(),
        )

        # Backstory button (only shown if backstory is available)
        backstory_button = ft.ElevatedButton(
            content=ft.Text("Backstory", size=18),
            width=button_width,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.PURPLE_300,
            ),
            on_click=self._show_backstory_dialog,
            visible=self.backstory is not None,
        )

        # Game selector carousel
        self.game_selector = GameSelector(
            on_select_game=self.on_load_config,
            width=page_width - (padding_value * 2),
        )

        # Layout for mobile or desktop
        content = ft.Column(
            controls=[
                title,
                subtitle,
                ft.Container(height=20),  # Spacing
                # Game selector section
                ft.Text(
                    "Select a Game",
                    size=18,
                    color=ft.colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=10),
                self.game_selector,
                ft.Container(height=30),  # Spacing
                # Action buttons section
                ft.Text(
                    "Options", size=18, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD
                ),
                ft.Container(height=10),
                settings_button,
                # Only add backstory button if backstory exists
                ft.Container(height=20, visible=self.backstory is not None),
                backstory_button,
                ft.Container(height=20),  # Bottom spacing
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
            ),
        )

    def _show_load_dialog(self, e: ft.ControlEvent) -> None:
        """Show dialog to load a configuration file"""
        # Create text field for file path or URL
        config_path_field = ft.TextField(
            label="Configuration file path or URL",
            hint_text="Enter file path or URL",
            width=400,
        )

        def close_dialog(load: bool = False) -> None:
            # Close the dialog
            if self.page and hasattr(self.page, "dialog"):
                self.page.dialog.open = False
                self.page.update()

            # If load button was clicked, call the load handler
            if load and config_path_field.value:
                self.on_load_config(config_path_field.value)

        # Create the dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Load Game Configuration"),
            content=ft.Column(
                [
                    ft.Text("Enter a file path or URL to a game configuration file:"),
                    config_path_field,
                    ft.Row([ft.FilePicker(on_result=self._handle_file_picker_result)]),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: close_dialog(False)),
                ft.TextButton("Load", on_click=lambda _: close_dialog(True)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # File picker for browsing local files
        def open_file_picker(_: ft.ControlEvent) -> None:
            if self.page and self.page.overlay and len(self.page.overlay) > 0:
                self.page.overlay[0].pick_files(
                    dialog_title="Select Game Configuration",
                    allowed_extensions=["json"],
                    file_type=ft.FilePickerFileType.CUSTOM,
                )

        # Add the browse button
        browse_button = ft.ElevatedButton(
            "Browse Files", icon=ft.icons.FOLDER_OPEN, on_click=open_file_picker
        )

        dialog.content.controls.append(browse_button)

        # Register the file picker
        if self.page and hasattr(self.page, "overlay"):
            if not self.page.overlay:
                self.page.overlay.append(
                    ft.FilePicker(on_result=self._handle_file_picker_result)
                )

            # Show the dialog
            if hasattr(self.page, "dialog"):
                self.page.dialog = dialog
                self.page.dialog.open = True
                self.page.update()

    def _handle_file_picker_result(self, e: ft.FilePickerResultEvent) -> None:
        """Handle the file picker result"""
        if e.files and len(e.files) > 0:
            # Get the selected file path
            file_path = e.files[0].path

            # Update the text field in the dialog
            if (
                self.page
                and hasattr(self.page, "dialog")
                and self.page.dialog
                and hasattr(self.page.dialog, "content")
            ):
                for control in self.page.dialog.content.controls:
                    if isinstance(control, ft.TextField):
                        control.value = file_path
                        break

                self.page.dialog.update()

    def _show_backstory_dialog(self, e: ft.ControlEvent) -> None:
        """Show dialog with game backstory"""
        if not self.backstory:
            return

        # Create scrollable content for the backstory text
        backstory_text = ft.SelectionArea(
            content=ft.Text(
                self.backstory,
                size=16,
                text_align=ft.TextAlign.LEFT,
            )
        )

        # Wrap in a scrollable container
        scrollable_content = ft.Container(
            content=backstory_text,
            padding=10,
            height=400,  # Fixed height for the content area
        )

        # Create the dialog with scrolling
        dialog = ft.AlertDialog(
            title=ft.Text("Backstory", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    scrollable_content,
                ],
                scroll=ft.ScrollMode.AUTO,  # Enable scrolling
                height=400,
                width=500,
            ),
            actions=[
                ft.TextButton("Close", on_click=self._close_backstory_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show the dialog
        if self.page and hasattr(self.page, "dialog"):
            self.page.dialog = dialog
            self.page.dialog.open = True
            self.page.update()

    def _close_backstory_dialog(self, e: ft.ControlEvent) -> None:
        """Close the backstory dialog"""
        if self.page and hasattr(self.page, "dialog"):
            self.page.dialog.open = False
            self.page.update()
