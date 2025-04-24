from typing import Any, Callable, Dict, List, Optional

import flet as ft

from swipe_verse.models.game_state import GameState
from swipe_verse.services.game_logic import GameLogic
from swipe_verse.ui.achievements_screen import AchievementsScreen
from swipe_verse.ui.components.card_display import CardDisplay
from swipe_verse.ui.components.resource_bar import ResourceBar


# Note: For Flet 0.27.x compatibility
# We're using a standard class instead of UserControl which is only in newer Flet versions
class GameScreen:
    def __init__(
        self,
        game_state: GameState,
        game_logic: GameLogic,
        on_new_game: Optional[Callable[[], Any]] = None,
        on_main_menu: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.game_state = game_state
        self.game_logic = game_logic
        self.on_new_game = on_new_game
        self.on_main_menu = on_main_menu
        self.card_display: Optional[CardDisplay] = None
        self.resource_bar: Optional[ResourceBar] = None
        self.page: Optional[ft.Page] = None
        self.controls: List[ft.Control] = [] # List to hold the main layout control
        self.main_column: Optional[ft.Column] = None # Reference to the main column for updates

    def build(self) -> ft.Column:
        """Build the game screen with all its components"""

        # Resource Bar
        resource_icons_str: Dict[str, str] = {
            k: str(v) for k, v in self.game_state.theme.resource_icons.items()
        }
        self.resource_bar = ResourceBar(
            resources=self.game_state.resources,
            resource_icons=resource_icons_str,
            max_resources=self.game_state.settings.initial_resources,
        )

        # Card Display (handles title, text, image, and swipe overlays)
        from swipe_verse.models.card import Card as ModelCard
        from swipe_verse.models.card import CardChoice as ModelCardChoice

        # Ensure current_card has choices before accessing them
        choices_dict = {}
        if self.game_state.current_card.choices:
            choices_dict = {
                k: ModelCardChoice(
                    text=v.text, effects=v.effects, next_card=v.next_card
                )
                for k, v in self.game_state.current_card.choices.items()
            }

        current_card = ModelCard(
            id=self.game_state.current_card.id,
            title=self.game_state.current_card.title,
            text=self.game_state.current_card.text,
            image=self.game_state.current_card.image,
            choices=choices_dict,
        )

        self.card_display = CardDisplay(
            current_card,
            on_swipe_left=self._handle_swipe_left,
            on_swipe_right=self._handle_swipe_right,
        )

        # Game Stats Section
        game_stats = self._create_game_stats()

        # Menu Buttons
        menu_buttons = ft.Row(
            [
                ft.ElevatedButton(
                    "Achievements",
                    on_click=lambda _: self._show_achievements(),
                    icon=ft.icons.EMOJI_EVENTS,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.PURPLE_500,
                    ),
                ),
                ft.ElevatedButton(
                    "New Game",
                    on_click=lambda _: self.on_new_game() if self.on_new_game else None,
                    icon=ft.icons.REPLAY,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_500,
                    ),
                ),
                ft.ElevatedButton(
                    "Main Menu",
                    on_click=lambda _: self.on_main_menu() if self.on_main_menu else None,
                    icon=ft.icons.HOME,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_700,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        # --- Main Layout Column --- 
        # Removed card_text, card_title, and decision_buttons as they are now part of CardDisplay
        # or implicitly handled by swipe
        self.main_column = ft.Column(
            controls=[
                self.resource_bar.build(), # Top: Resource bar
                self.card_display,       # Middle: The interactive card display
                game_stats,             # Below Card: Game statistics
                ft.Container(height=20),  # Spacing
                menu_buttons,           # Bottom: Menu buttons
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, # Distribute space
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            expand=True,
        )

        # Store the main column for potential direct updates
        self.controls = [self.main_column]

        return self.main_column

    def _create_game_stats(self) -> ft.Container:
        """Create a container with game statistics"""
        popularity = self.game_logic.calculate_popularity()
        turn_text = f"{self.game_state.turn_count} {self.game_state.settings.turn_unit}"
        progress = self.game_logic.calculate_progress()

        stats_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(f"Player: {self.game_state.player_name}", size=14),
                            ft.Text(f"Turns: {turn_text}", size=14),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text(f"Popularity: {popularity}%", size=14),
                            ft.Text(f"Progress: {progress}%", size=14),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ]
            ),
            padding=10,
            border_radius=5,
            bgcolor=ft.colors.BLACK12,
            # Ensure stats container doesn't stretch unnecessarily wide
            width=350 * 0.9, # Match card width approx
            alignment=ft.alignment.center,
        )
        return stats_container

    def _handle_swipe_left(self, e: Optional[ft.ControlEvent] = None) -> None: # Allow optional event arg
        """Process the left swipe action"""
        self._process_choice("left")

    def _handle_swipe_right(self, e: Optional[ft.ControlEvent] = None) -> None: # Allow optional event arg
        """Process the right swipe action"""
        self._process_choice("right")

    def _process_choice(self, direction: str) -> None:
        """Process the player's choice and update the game state"""
        # Check if there's a valid choice for the direction
        if not self.game_state.current_card.choices or direction not in self.game_state.current_card.choices:
            print(f"Warning: No valid choice for direction '{direction}' on card {self.game_state.current_card.id}")
            return # Don't process if the choice doesn't exist

        result = self.game_logic.process_choice(direction)

        # Update Resource Bar
        if self.resource_bar:
            self.resource_bar.update_all_resources(self.game_state.resources)

        # Update Card Display (it handles its own title/text/image update)
        if self.card_display:
            from swipe_verse.models.card import Card as ModelCard
            from swipe_verse.models.card import CardChoice as ModelCardChoice
            
            # Ensure next card has choices before accessing them
            next_choices_dict = {}
            if self.game_state.current_card.choices:
                 next_choices_dict = {
                     k: ModelCardChoice(
                         text=v.text, effects=v.effects, next_card=v.next_card
                     )
                     for k, v in self.game_state.current_card.choices.items()
                 }

            next_card = ModelCard(
                id=self.game_state.current_card.id,
                title=self.game_state.current_card.title,
                text=self.game_state.current_card.text,
                image=self.game_state.current_card.image,
                choices=next_choices_dict,
            )
            self.card_display.update_card(next_card)

        # Update Game Stats (find the stats container and update it)
        if self.main_column:
            for i, control in enumerate(self.main_column.controls):
                 # Identify the stats container (assuming it's a Container with specific content)
                 # This check might need refinement based on exact structure
                 if isinstance(control, ft.Container) and isinstance(control.content, ft.Column) and len(control.content.controls) == 2:
                      # Found a likely candidate for the stats container
                      new_stats = self._create_game_stats()
                      self.main_column.controls[i] = new_stats # Replace the old stats container
                      break # Stop searching once found
            else: # If loop finished without break
                print("Warning: Could not find game stats container to update.")

        # --- Removed update logic for separate card_text, card_title, decision_buttons ---

        # Update the entire page
        if self.page:
            self.page.update()

        # Check for game over
        if result.game_over:
            self._show_game_over_dialog(result.message, result.summary)

    def _show_game_over_dialog(
        self, message: str, game_summary: Optional[Dict[str, Any]] = None
    ) -> None:
        """Show game over dialog with the result message and achievements"""

        def start_new_game(_: ft.ControlEvent) -> None:
            if self.page:
                self.page.dialog.open = False
                self.page.update()
            if self.on_new_game:
                self.on_new_game()

        def go_to_title(_: ft.ControlEvent) -> None:
            if self.page:
                self.page.dialog.open = False
                self.page.update()
            if self.on_main_menu:
                self.on_main_menu()

        def view_achievements(_: ft.ControlEvent) -> None:
            if self.page:
                self.page.dialog.open = False
                self.page.update()
                self._show_achievements()

        # Create content with basic game info
        content_controls = [
            ft.Text(message, size=18, weight=ft.FontWeight.BOLD),
            ft.Text(
                f"You lasted {self.game_state.turn_count} "
                f"{self.game_state.settings.turn_unit}."
            ),
            ft.Text(f"Popularity: {self.game_logic.calculate_popularity()}%"),
            ft.Divider(height=1, color=ft.colors.BLACK26),
        ]

        # Add achievement notifications if any were unlocked
        if (
            game_summary
            and "new_achievements" in game_summary
            and game_summary["new_achievements"]
        ):
            content_controls.append(
                ft.Text(
                    "Achievements Unlocked!",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.AMBER,
                )
            )

            for achievement in game_summary["new_achievements"]:
                achievement_row = ft.Row(
                    [
                        ft.Text(achievement["icon"], size=20),
                        ft.Text(
                            achievement["name"], size=14, weight=ft.FontWeight.BOLD
                        ),
                    ]
                )
                content_controls.append(achievement_row)
                content_controls.append(
                    ft.Text(
                        achievement["description"], size=12, color=ft.colors.BLACK54
                    )
                )

            content_controls.append(ft.Divider(height=1, color=ft.colors.BLACK26))

        # Create the dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Game Over"),
            content=ft.Column(content_controls, tight=True, spacing=10),
            actions=[
                ft.ElevatedButton("New Game", on_click=start_new_game),
                ft.OutlinedButton("Main Menu", on_click=go_to_title),
                ft.ElevatedButton("View Achievements", on_click=view_achievements),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show the dialog
        if self.page:
            self.page.dialog = dialog
            self.page.dialog.open = True
            self.page.update()

    def update(self) -> None:
        """Explicitly update the page if needed (might not be necessary if updates happen in handlers)"""
        if self.page:
            self.page.update()

    def _show_achievements(self) -> None:
        """Show achievements and statistics screen"""
        if self.page:
            achievements_screen = AchievementsScreen(
                game_logic=self.game_logic,
                on_back=lambda: self._return_from_achievements(),
            )
            achievements_screen.page = self.page
            self._saved_screen = self.page.controls[0] # Save current screen view
            self.page.controls[0] = achievements_screen.build()
            self.page.update()

    def _return_from_achievements(self) -> None:
        """Return from achievements screen to game screen"""
        if self.page and hasattr(self, "_saved_screen"):
            self.page.controls[0] = self._saved_screen # Restore saved screen view
            self.page.update()
