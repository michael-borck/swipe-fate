from typing import Any, Callable, Optional

import flet as ft

from swipe_verse.services.game_logic import GameLogic


class AchievementsScreen:
    """Screen to display achievements and game statistics."""

    def __init__(
        self,
        game_logic: GameLogic,
        on_back: Callable[[], Any],
    ) -> None:
        self.game_logic = game_logic
        self.on_back = on_back
        self.page: Optional[ft.Page] = None

    def build(self) -> ft.Container:
        # Responsive design adjustments
        page_width = 800  # Default width
        if self.page and hasattr(self.page, "width") and self.page.width is not None:
            page_width = self.page.width

        is_mobile = page_width < 600
        padding_value = 20 if is_mobile else 40
        inner_width = page_width - (padding_value * 2)

        # Get achievements and statistics
        achievements = self.game_logic.get_achievements()
        statistics = self.game_logic.get_statistics()
        recent_games = self.game_logic.get_recent_games(5)

        # Header section
        header = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Achievements & Statistics",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                    ft.Text(
                        "Track your progress and unlock rewards",
                        size=16,
                        color=ft.colors.WHITE70,
                        italic=True,
                    ),
                ]
            ),
            margin=ft.margin.only(bottom=20),
        )

        # Achievements section
        achievements_cards = []
        for achievement in achievements:
            achievement_card = ft.Container(
                content=ft.Row(
                    [
                        # Achievement icon
                        ft.Container(
                            content=ft.Text(
                                achievement["icon"],
                                size=24,
                            ),
                            width=40,
                            height=40,
                            border_radius=ft.border_radius.all(20),
                            bgcolor=ft.colors.with_opacity(
                                0.2,
                                ft.colors.WHITE
                                if achievement["unlocked"]
                                else ft.colors.GREY,
                            ),
                            alignment=ft.alignment.center,
                        ),
                        # Achievement details
                        ft.Column(
                            [
                                ft.Text(
                                    achievement["name"],
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.WHITE
                                    if achievement["unlocked"]
                                    else ft.colors.WHITE60,
                                ),
                                ft.Text(
                                    achievement["description"],
                                    size=12,
                                    color=ft.colors.WHITE70
                                    if achievement["unlocked"]
                                    else ft.colors.WHITE30,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        # Locked/Unlocked status
                        ft.Container(
                            content=ft.Icon(
                                ft.icons.LOCK_OPEN
                                if achievement["unlocked"]
                                else ft.icons.LOCK,
                                color=ft.colors.GREEN
                                if achievement["unlocked"]
                                else ft.colors.GREY_400,
                                size=20,
                            ),
                            width=40,
                        ),
                    ]
                ),
                width=inner_width,
                height=60,
                border_radius=ft.border_radius.all(8),
                bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                padding=ft.padding.all(10),
                margin=ft.margin.only(bottom=10),
            )
            achievements_cards.append(achievement_card)

        achievements_section = ft.Column(
            controls=[
                ft.Text(
                    "Achievements",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                ),
                ft.Text(
                    f"Unlocked: {statistics['achievements_unlocked']}/{statistics['total_achievements']}",
                    size=14,
                    color=ft.colors.WHITE70,
                ),
                ft.Container(height=10),  # Spacing
                *achievements_cards,
            ],
            spacing=5,
        )

        # Statistics section
        stats_cards = []

        # Game stats
        game_stats_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Game Statistics",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                    ft.Divider(height=1, color=ft.colors.WHITE24),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        "Total Games", size=12, color=ft.colors.WHITE70
                                    ),
                                    ft.Text(
                                        str(statistics["total_games"]),
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                expand=1,
                            ),
                            ft.Column(
                                [
                                    ft.Text("Wins", size=12, color=ft.colors.WHITE70),
                                    ft.Text(
                                        str(statistics["wins"]),
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                expand=1,
                            ),
                            ft.Column(
                                [
                                    ft.Text("Losses", size=12, color=ft.colors.WHITE70),
                                    ft.Text(
                                        str(statistics["losses"]),
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                expand=1,
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        "Win Rate", size=12, color=ft.colors.WHITE70
                                    ),
                                    ft.Text(
                                        f"{statistics['win_percentage']}%",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                expand=1,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Avg. Turns", size=12, color=ft.colors.WHITE70
                                    ),
                                    ft.Text(
                                        str(statistics["average_turns"]),
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                expand=1,
                            ),
                            ft.Column(
                                [
                                    ft.Text("", size=12, color=ft.colors.WHITE70),
                                    ft.Text("", size=18, weight=ft.FontWeight.BOLD),
                                ],
                                expand=1,
                            ),
                        ]
                    ),
                ]
            ),
            width=inner_width,
            border_radius=ft.border_radius.all(10),
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            padding=ft.padding.all(15),
            margin=ft.margin.only(bottom=10),
        )
        stats_cards.append(game_stats_card)

        # Best resource values
        resource_bars = []
        for resource, value in statistics.get("best_resources", {}).items():
            resource_bar = ft.Column(
                [
                    ft.Text(resource.capitalize(), size=12, color=ft.colors.WHITE70),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    width=value * (inner_width * 0.7) / 100,
                                    height=20,
                                    bgcolor=self._get_resource_color(resource),
                                    border_radius=ft.border_radius.all(4),
                                ),
                                ft.Container(width=10),  # Spacing
                                ft.Text(str(value), size=14, weight=ft.FontWeight.BOLD),
                            ]
                        ),
                    ),
                ]
            )
            resource_bars.append(resource_bar)

        if resource_bars:
            resource_stats_card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Best Resource Values",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE,
                        ),
                        ft.Divider(height=1, color=ft.colors.WHITE24),
                        *resource_bars,
                    ]
                ),
                width=inner_width,
                border_radius=ft.border_radius.all(10),
                bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                padding=ft.padding.all(15),
                margin=ft.margin.only(bottom=10),
            )
            stats_cards.append(resource_stats_card)

        # Recent games
        if recent_games:
            recent_game_items = []
            for game in recent_games:
                # Format date to a more readable format
                date_str = game["date"].split("T")[0]  # Simple date extraction

                game_item = ft.Container(
                    content=ft.Row(
                        [
                            # Win/loss indicator
                            ft.Container(
                                content=ft.Icon(
                                    ft.icons.CHECK_CIRCLE
                                    if game["won"]
                                    else ft.icons.CANCEL,
                                    color=ft.colors.GREEN
                                    if game["won"]
                                    else ft.colors.RED,
                                    size=20,
                                ),
                                width=30,
                            ),
                            # Game details
                            ft.Column(
                                [
                                    ft.Text(
                                        f"{game['theme']} - {date_str}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"Turns: {game['turns']} | Difficulty: {game['difficulty'].capitalize()}",
                                        size=12,
                                        color=ft.colors.WHITE70,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ]
                    ),
                    width=inner_width,
                    height=50,
                    border_radius=ft.border_radius.all(8),
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                    padding=ft.padding.all(10),
                    margin=ft.margin.only(bottom=5),
                )
                recent_game_items.append(game_item)

            recent_games_card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Recent Games",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE,
                        ),
                        ft.Divider(height=1, color=ft.colors.WHITE24),
                        *recent_game_items,
                    ]
                ),
                width=inner_width,
                border_radius=ft.border_radius.all(10),
                bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
                padding=ft.padding.all(15),
                margin=ft.margin.only(bottom=10),
            )
            stats_cards.append(recent_games_card)

        statistics_section = ft.Column(
            controls=[
                ft.Text(
                    "Statistics",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                ),
                ft.Container(height=10),  # Spacing
                *stats_cards,
            ],
            spacing=5,
        )

        # Back button
        back_button = ft.ElevatedButton(
            content=ft.Text("Back to Game", size=16),
            width=200,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_700,
            ),
            on_click=lambda _: self.on_back(),
        )

        # Main layout
        content = ft.Column(
            controls=[
                header,
                ft.Container(
                    content=ft.Column(
                        [
                            achievements_section,
                            ft.Container(height=20),  # Spacing
                            statistics_section,
                        ]
                    ),
                    padding=ft.padding.all(20),
                    border_radius=ft.border_radius.all(10),
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                ),
                ft.Container(height=20),  # Spacing
                ft.Row([back_button], alignment=ft.MainAxisAlignment.CENTER),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        )

        # Main container with background gradient
        return ft.Container(
            content=content,
            expand=True,
            padding=padding_value,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[ft.colors.BLUE_900, ft.colors.INDIGO_900],
            ),
        )

    def _get_resource_color(self, resource: str) -> Any:
        """Get a color for a specific resource."""
        colors = {
            "treasury": ft.colors.AMBER,
            "population": ft.colors.GREEN,
            "military": ft.colors.RED,
            "church": ft.colors.PURPLE,
            "finances": ft.colors.AMBER,
            "employees": ft.colors.GREEN,
            "innovation": ft.colors.BLUE,
            "reputation": ft.colors.PURPLE,
            "knowledge": ft.colors.BLUE,
            "energy": ft.colors.RED,
            "time": ft.colors.GREEN,
            "mood": ft.colors.PURPLE,
        }
        return colors.get(resource.lower(), ft.colors.BLUE)
