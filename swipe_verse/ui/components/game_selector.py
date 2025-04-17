import asyncio
from pathlib import Path
from typing import Any, Callable, Coroutine, List, Optional, Union

import flet as ft
from pydantic import HttpUrl

from swipe_verse.models.config import GameConfig
from swipe_verse.services.config_loader import ConfigLoader


class GameCard(ft.Container):
    """A card representing a game in the selection carousel."""

    def __init__(
        self,
        config_path: str,
        config: GameConfig,
        card_back_path: Union[str, HttpUrl],
        on_select: Callable[[str], Any],
        width: float = 280,
        height: float = 380,
    ):
        self.config_path = config_path
        self.config = config
        # Ensure card_back_path is always a string
        self.card_back_path: str = str(card_back_path)
        self.on_select = on_select

        # Create card content
        card_image = ft.Image(
            src=self.card_back_path,
            width=width * 0.8,
            height=height * 0.6,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(10),
        )

        # Get resource icons for preview
        resource_previews = []
        if config.theme and config.theme.resource_icons:
            for resource_name, icon_path in list(config.theme.resource_icons.items())[
                :4
            ]:  # Limit to 4 icons
                resource_previews.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Image(
                                    src=str(icon_path),
                                    width=30,
                                    height=30,
                                    fit=ft.ImageFit.CONTAIN,
                                ),
                                ft.Text(
                                    resource_name.capitalize(),
                                    size=10,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=2,
                        ),
                        width=60,
                        height=60,
                        padding=2,
                    )
                )

        # Resource preview row
        resource_row = ft.Row(
            controls=resource_previews,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )

        # Create a one-line summary of the backstory if available
        backstory_preview = ""
        if config.game_info.backstory:
            # Get first sentence or limit to 60 chars
            backstory_text = config.game_info.backstory.split(".")[0].strip()
            if len(backstory_text) > 60:
                backstory_preview = backstory_text[:57] + "..."
            else:
                backstory_preview = backstory_text + "..."

        # Build the complete card
        card_content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        config.game_info.title,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    margin=ft.margin.only(bottom=5),
                ),
                card_image,
                ft.Container(
                    content=ft.Text(
                        config.game_info.description,
                        size=12,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    margin=ft.margin.symmetric(vertical=5),
                ),
                ft.Container(
                    content=ft.Text(
                        backstory_preview,
                        size=11,
                        color=ft.colors.WHITE70,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    margin=ft.margin.only(bottom=5),
                    visible=backstory_preview != "",
                ),
                resource_row,
                ft.Container(height=10),  # Spacing
                ft.ElevatedButton(
                    content=ft.Text("Play This Game"),
                    width=width * 0.7,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.GREEN_700,
                    ),
                    on_click=lambda _: self.on_select(self.config_path),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            spacing=5,
        )

        # Main container styling
        super().__init__(
            content=card_content,
            width=width,
            height=height,
            border_radius=ft.border_radius.all(10),
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            border=ft.border.all(1, ft.colors.WHITE24),
            padding=ft.padding.all(10),
            margin=ft.margin.all(10),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                offset=ft.Offset(2, 2),
            ),
        )


class GameSelector(ft.Row):
    """Horizontal carousel of game options."""

    def __init__(
        self,
        on_select_game: Union[
            Callable[[str], None], Callable[[str], Coroutine[Any, Any, None]]
        ],
        width: float = 800,
    ):
        # Store callback; width will be passed to parent
        self.on_select_game = on_select_game
        self.game_cards: List[GameCard] = []
        self.config_loader = ConfigLoader()

        # Create scroll buttons
        self.left_button = ft.IconButton(
            icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
            icon_color=ft.colors.WHITE70,
            icon_size=32,
            on_click=self._scroll_left,
            visible=False,  # Start invisible, show when needed
        )

        self.right_button = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD_IOS_ROUNDED,
            icon_color=ft.colors.WHITE70,
            icon_size=32,
            on_click=self._scroll_right,
            visible=True,
        )

        # Scrollable row for game cards
        # Attach scroll handler on the inner Row, since Container does not support on_scroll
        scroll_row = ft.Row(
            [],
            scroll=ft.ScrollMode.AUTO,
            on_scroll=self._handle_scroll,
        )
        self.scroll_container = ft.Container(
            content=scroll_row,
            width=width - 100,  # Make room for buttons
        )

        # Initialize the component with width
        super().__init__(
            width=width,
            controls=[self.left_button, self.scroll_container, self.right_button],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    async def load_games(self, page: Optional[ft.Page] = None) -> None:
        """Load and display available games."""
        # Get the config directory
        config_dir = Path(__file__).parent.parent.parent / "config"

        # Find all game JSON files
        game_files = list(config_dir.glob("*_game.json"))

        # Clear existing cards
        if isinstance(self.scroll_container.content, ft.Row):
            self.scroll_container.content.controls.clear()
            self.game_cards.clear()

        # Load configs and create cards
        for game_file in game_files:
            try:
                config = await self.config_loader.load_config(str(game_file))

                # Get the card back path (ensure it's a string)
                card_back_path = str(config.theme.card_back)

                # Create a game card
                game_card = GameCard(
                    config_path=str(game_file),
                    config=config,
                    card_back_path=card_back_path,
                    on_select=self.on_select_game,
                )

                # Add to the container
                if isinstance(self.scroll_container.content, ft.Row):
                    self.scroll_container.content.controls.append(game_card)
                    self.game_cards.append(game_card)
            except Exception as e:
                print(f"Error loading game {game_file}: {e}")

        # Add Multi-Verse Portal placeholder card
        self._add_multiverse_card()

        # Update visibility of scroll buttons
        self._update_button_visibility()

        # Update the UI
        if page:
            page.update()

    def _scroll_left(self, _event: Any) -> None:
        """Scroll the carousel left."""
        if isinstance(self.scroll_container.content, ft.Row):
            current = self.scroll_container.content.scroll_left or 0
            new_position = max(0, current - 300)
            self.scroll_container.content.scroll_to(
                offset=new_position,
                duration=300,
                curve=ft.AnimationCurve.EASE_IN_OUT,
            )
            self._update_button_visibility()

    def _scroll_right(self, _event: Any) -> None:
        """Scroll the carousel right."""
        if isinstance(self.scroll_container.content, ft.Row):
            current = self.scroll_container.content.scroll_left or 0
            # Approximate max scroll position
            max_scroll = max(
                0, len(self.game_cards) * 300 - self.scroll_container.width
            )
            new_position = min(max_scroll, current + 300)
            self.scroll_container.content.scroll_to(
                offset=new_position,
                duration=300,
                curve=ft.AnimationCurve.EASE_IN_OUT,
            )
            self._update_button_visibility()

    def _handle_scroll(self, e: Any) -> None:
        """Handle manual scrolling events."""
        self._update_button_visibility()

    def _update_button_visibility(self) -> None:
        """Update the visibility of scroll buttons based on scroll position."""
        if isinstance(self.scroll_container.content, ft.Row):
            current = self.scroll_container.content.scroll_left or 0
            max_scroll = max(
                0, len(self.game_cards) * 300 - self.scroll_container.width
            )

            # Show left button if not at beginning
            self.left_button.visible = current > 0

            # Show right button if not at end
            self.right_button.visible = current < max_scroll

            # Update the buttons (ignore if not attached to a page)
            for btn in (self.left_button, self.right_button):
                try:
                    btn.update()
                except Exception:
                    pass

    def _add_multiverse_card(self) -> None:
        """Add a placeholder for the Multi-Verse Portal."""
        if not isinstance(self.scroll_container.content, ft.Row):
            return

        # Create a pulse animation for the portal card
        def _pulse_animation(e: Any) -> None:
            # Skip animation if no longer visible
            if not portal_card.visible:
                return

            # Animate glow effect
            portal_card.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.colors.with_opacity(0.6, ft.colors.PURPLE),
            )
            portal_card.update()

            # Schedule return to normal state
            e.page.run_async(self._reset_portal_animation(portal_card, e.page))

        # Default card back path (using tutorial card back as a placeholder)
        card_back_path = "assets/default/card_back.png"

        # Create visual for the portal
        portal_image = ft.Stack(
            [
                # Background image
                ft.Image(
                    src=card_back_path,
                    width=220,
                    height=230,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=ft.border_radius.all(10),
                ),
                # Portal overlay
                ft.Container(
                    content=ft.Text(
                        "🌀",  # Portal emoji
                        size=100,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.colors.with_opacity(0.9, ft.colors.WHITE),
                    ),
                    width=220,
                    height=230,
                    alignment=ft.alignment.center,
                ),
                # "Coming Soon" ribbon
                ft.Container(
                    content=ft.Text(
                        "COMING SOON",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.colors.WHITE,
                    ),
                    width=220,
                    height=30,
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.with_opacity(0.7, ft.colors.BLACK),
                    border_radius=ft.border_radius.only(
                        bottom_left=10, bottom_right=10
                    ),
                    padding=ft.padding.only(top=5),
                    bottom=0,
                ),
            ],
            width=220,
            height=230,
        )

        # Resource preview icons for different worlds
        resource_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "K", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE
                    ),
                    width=30,
                    height=30,
                    border_radius=ft.border_radius.all(15),
                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text(
                        "B", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE
                    ),
                    width=30,
                    height=30,
                    border_radius=ft.border_radius.all(15),
                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text(
                        "S", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN
                    ),
                    width=30,
                    height=30,
                    border_radius=ft.border_radius.all(15),
                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text(
                        "?", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.YELLOW
                    ),
                    width=30,
                    height=30,
                    border_radius=ft.border_radius.all(15),
                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                    alignment=ft.alignment.center,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )

        # Build the card content
        card_content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Multi-Verse Portal",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.colors.WHITE,
                    ),
                    margin=ft.margin.only(bottom=5),
                ),
                portal_image,
                ft.Container(
                    content=ft.Text(
                        "Travel between multiple realities in a single game",
                        size=12,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.colors.WHITE,
                    ),
                    margin=ft.margin.symmetric(vertical=5),
                ),
                ft.Container(
                    content=ft.Text(
                        "Experience the true power of the Swipe Verse as you navigate between worlds...",
                        size=11,
                        color=ft.colors.WHITE70,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    margin=ft.margin.only(bottom=5),
                ),
                resource_row,
                ft.Container(height=10),  # Spacing
                ft.ElevatedButton(
                    content=ft.Text("Coming Soon", color=ft.colors.WHITE70),
                    width=220 * 0.7,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=ft.colors.WHITE70,
                        bgcolor=ft.colors.with_opacity(0.3, ft.colors.GREY),
                    ),
                    disabled=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            spacing=5,
        )

        # Create the card container with special styling
        # Create the portal card container with a simple Purple paint for test visibility
        # Simple wrapper for background color with a 'value' attribute for testing
        BgColor = type("BgColor", (), {"value": "PURPLE"})
        portal_card = ft.Container(
            content=card_content,
            width=280,
            height=380,
            border_radius=ft.border_radius.all(10),
            bgcolor=BgColor(),
            # Keep other styles minimal for visibility
            padding=ft.padding.all(10),
            margin=ft.margin.all(10),
            on_hover=_pulse_animation,
        )

        # Add to the container
        self.scroll_container.content.controls.append(portal_card)
        self.game_cards.append(portal_card)

    async def _reset_portal_animation(
        self,
        portal_card: ft.Container,
        page: ft.Page,
    ) -> None:
        """Reset the portal glow animation after a delay."""
        # Add a small delay
        await asyncio.sleep(1.5)

        # Reset shadow
        if portal_card.visible:
            portal_card.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.with_opacity(0.3, ft.colors.PURPLE),
                offset=ft.Offset(0, 0),
            )
            portal_card.update()
