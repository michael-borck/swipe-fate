from typing import Callable, Optional, Any

import flet as ft

from swipe_fate.models.card import Card


# Note: For Flet 0.27.x compatibility, we extend GestureDetector instead of UserControl
class CardDisplay(ft.GestureDetector):
    def __init__(
        self, 
        card: Card, 
        on_swipe_left: Optional[Callable[[ft.DragEndEvent], None]] = None, 
        on_swipe_right: Optional[Callable[[ft.DragEndEvent], None]] = None, 
        **kwargs: Any
    ) -> None:
        self.card = card
        self.on_swipe_left = on_swipe_left
        self.on_swipe_right = on_swipe_right
        self.swipe_threshold = 50  # Minimum distance to count as a swipe
        self.is_swiping = False
        self.start_x = 0
        self.current_x = 0
        self.card_container: Optional[ft.Container] = None
        self.card_image: Optional[ft.Image] = None

        super().__init__(
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            **kwargs,
        )

    def build(self) -> ft.Container:
        # Responsive sizing
        page_width = 300
        if self.page and hasattr(self.page, 'width') and self.page.width is not None:
            page_width = self.page.width
            
        container_width = min(350, page_width * 0.8)
        container_height = container_width * 1.5  # 3:2 aspect ratio

        # Card image
        self.card_image = ft.Image(
            src=self.card.image,
            width=container_width,
            height=container_height,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.all(10),
        )

        # The card container that will be animated during swipe
        self.card_container = ft.Container(
            content=self.card_image,
            width=container_width,
            height=container_height,
            border_radius=ft.border_radius.all(10),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.BLACK26,
                offset=ft.Offset(2, 2),
            ),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            alignment=ft.alignment.center,
        )

        # Center the card in the container
        return ft.Container(
            content=self.card_container,
            width=container_width,
            height=container_height,
            alignment=ft.alignment.center,
        )

    def _on_pan_start(self, e: ft.DragStartEvent) -> None:
        """Handle the start of a swipe gesture"""
        self.is_swiping = True
        self.start_x = e.local_x
        self.current_x = e.local_x

    def _on_pan_update(self, e: ft.DragUpdateEvent) -> None:
        """Handle ongoing swipe gesture updates"""
        if not self.is_swiping or not self.card_container:
            return

        self.current_x = e.local_x
        delta_x = self.current_x - self.start_x

        # Limit the drag distance
        max_drag = 100
        if abs(delta_x) > max_drag:
            delta_x = max_drag if delta_x > 0 else -max_drag

        # Update the card position
        self.card_container.offset = ft.transform.Offset(delta_x / 100, 0)

        # Add rotation based on the drag distance
        angle = (delta_x / 100) * 0.2  # Reduce rotation amount
        self.card_container.rotate = ft.transform.Rotate(angle)

        # Add opacity change to indicate the swipe direction
        if delta_x > 20:  # Right swipe - positive choice
            self.card_container.border = ft.border.all(2, ft.colors.GREEN)
        elif delta_x < -20:  # Left swipe - negative choice
            self.card_container.border = ft.border.all(2, ft.colors.RED)
        else:
            self.card_container.border = None

        self.update()

    def _on_pan_end(self, e: ft.DragEndEvent) -> None:
        """Handle the end of a swipe gesture"""
        if not self.is_swiping or not self.card_container:
            return

        self.is_swiping = False
        delta_x = self.current_x - self.start_x

        # Reset the card position with animation
        self.card_container.offset = ft.transform.Offset(0, 0)
        self.card_container.rotate = ft.transform.Rotate(0)
        self.card_container.border = None
        self.update()

        # Check if the swipe was decisive enough
        if abs(delta_x) > self.swipe_threshold:
            if delta_x > 0 and self.on_swipe_right:
                self.on_swipe_right(e)
            elif delta_x < 0 and self.on_swipe_left:
                self.on_swipe_left(e)

    def update_card(self, card: Card) -> None:
        """Update the card being displayed"""
        self.card = card
        # Update the image
        if self.card_image:
            self.card_image.src = card.image
            # Force update
            self.update()
