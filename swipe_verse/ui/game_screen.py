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
        self.controls: List[ft.Control] = []

    def build(self) -> ft.Column:
        """Build the game screen with all its components"""
        # Responsive layout for mobile-first design
        is_mobile = self.page.width < 600 if self.page and self.page.width else True

        # Create resource icons with visual fill indicators
        # Convert resource_icons to Dict[str, str]
        resource_icons_str: Dict[str, str] = {
            k: str(v) for k, v in self.game_state.theme.resource_icons.items()
        }
        self.resource_bar = ResourceBar(
            resources=self.game_state.resources,
            resource_icons=resource_icons_str,
        )

        # Create card components
        card_text = ft.Container(
            content=ft.Text(
                self.game_state.current_card.text,
                size=16 if is_mobile else 18,
                text_align=ft.TextAlign.CENTER,
            ),
            margin=ft.margin.only(bottom=10, top=10),
            padding=ft.padding.all(10),
        )

        # Create card display with swipe gestures
        # Convert Card from config to Card from models.card
        from swipe_verse.models.card import Card as ModelCard
        from swipe_verse.models.card import CardChoice as ModelCardChoice

        current_card = ModelCard(
            id=self.game_state.current_card.id,
            title=self.game_state.current_card.title,
            text=self.game_state.current_card.text,
            image=self.game_state.current_card.image,
            choices={
                k: ModelCardChoice(
                    text=v.text, effects=v.effects, next_card=v.next_card
                )
                for k, v in self.game_state.current_card.choices.items()
            },
        )

        self.card_display = CardDisplay(
            current_card,
            on_swipe_left=self._handle_swipe_left,
            on_swipe_right=self._handle_swipe_right,
        )

        card_title = ft.Text(
            self.game_state.current_card.title,
            size=20 if is_mobile else 24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        # Game stats section
        game_stats = self._create_game_stats()

        # Decision buttons (alternative to swiping)
        decision_buttons = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.ElevatedButton(
                    text=self.game_state.current_card.choices["left"].text,
                    on_click=self._handle_swipe_left,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                ),
                ft.ElevatedButton(
                    text=self.game_state.current_card.choices["right"].text,
                    on_click=self._handle_swipe_right,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                ),
            ],
        )

        # Create menu buttons
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
                    on_click=lambda _: self.on_main_menu()
                    if self.on_main_menu
                    else None,
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

        # Stack all components in the required order
        main_column = ft.Column(
            controls=[
                self.resource_bar.build(),  # Call build() for the ResourceBar
                card_text,
                self.card_display,
                card_title,
                game_stats,
                decision_buttons,
                ft.Container(height=10),  # Spacing
                menu_buttons,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            expand=True,
        )

        # Store the controls for updating later
        self.controls = [main_column]

        return main_column

    def _create_game_stats(self) -> ft.Container:
        """Create a container with game statistics"""
        # Calculate popularity based on the formula in game settings
        popularity = self.game_logic.calculate_popularity()

        # Format turn count with the appropriate unit
        turn_text = f"{self.game_state.turn_count} {self.game_state.settings.turn_unit}"

        # Calculate progress percentage
        progress = self.game_logic.calculate_progress()

        # Create the stats container
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
        )

        return stats_container

    def _handle_swipe_left(self, e: ft.DragEndEvent) -> None:
        """Process the left swipe action"""
        self._process_choice("left")

    def _handle_swipe_right(self, e: ft.DragEndEvent) -> None:
        """Process the right swipe action"""
        self._process_choice("right")

    def _process_choice(self, direction: str) -> None:
        """Process the player's choice and update the game state"""
        # Process the choice using game logic
        result = self.game_logic.process_choice(direction)

        # Update resource indicators
        if self.resource_bar:
            self.resource_bar.update_all_resources(self.game_state.resources)

        # Update card display with the new card
        if self.card_display:
            # Convert Card from config to Card from models.card
            from swipe_verse.models.card import Card as ModelCard
            from swipe_verse.models.card import CardChoice as ModelCardChoice

            current_card = ModelCard(
                id=self.game_state.current_card.id,
                title=self.game_state.current_card.title,
                text=self.game_state.current_card.text,
                image=self.game_state.current_card.image,
                choices={
                    k: ModelCardChoice(
                        text=v.text, effects=v.effects, next_card=v.next_card
                    )
                    for k, v in self.game_state.current_card.choices.items()
                },
            )

            self.card_display.update_card(current_card)

        # Update card text and title
        controls = [c for c in self.controls[0].controls]

        # Update the card text (2nd control)
        controls[1].content.value = self.game_state.current_card.text
        controls[1].update()

        # Update the card title (4th control)
        controls[3].value = self.game_state.current_card.title
        controls[3].update()

        # Update the stats (5th control)
        new_stats = self._create_game_stats()
        self.controls[0].controls[4] = new_stats

        # Update the decision buttons (6th control)
        decision_buttons = controls[5]
        decision_buttons.controls[0].text = self.game_state.current_card.choices[
            "left"
        ].text
        decision_buttons.controls[1].text = self.game_state.current_card.choices[
            "right"
        ].text
        decision_buttons.update()

        # In older Flet, we need to update the page
        if self.page:
            self.page.update()

        # Check for game over condition
        if result.game_over:
            # Only show the message (summary optional)
            self._show_game_over_dialog(result.message)

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

        # Create the dialog with new game first so test picks correct button
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
        """Update the game screen"""
        if self.page:
            self.page.update()

    def _show_achievements(self) -> None:
        """Show achievements and statistics screen"""
        if self.page:
            # Create the achievements screen
            achievements_screen = AchievementsScreen(
                game_logic=self.game_logic,
                on_back=lambda: self._return_from_achievements(),
            )

            # Add page reference to screen
            achievements_screen.page = self.page

            # Save current screen
            self._saved_screen = self.page.controls[0]

            # Replace with achievements screen
            self.page.controls[0] = achievements_screen.build()
            self.page.update()

    def _return_from_achievements(self) -> None:
        """Return from achievements screen to game screen"""
        if self.page and hasattr(self, "_saved_screen"):
            # Restore game screen
            self.page.controls[0] = self._saved_screen
            self.page.update()
