import flet as ft
from typing import Dict, Any, Callable, Optional

class DecisionCard(ft.UserControl):
    def __init__(
        self, 
        decision_data: Dict[str, Any], 
        on_swipe_left: Callable[[], None], 
        on_swipe_right: Callable[[], None],
        card_width: int = 320,
        card_height: int = 420,
    ):
        super().__init__()
        self.decision_data = decision_data
        self.on_swipe_left = on_swipe_left
        self.on_swipe_right = on_swipe_right
        self.card_width = card_width
        self.card_height = card_height
        self.drag_x = 0
        self.rotation = 0
        self.opacity = 1.0
        
        self.animation = ft.Animation(500, ft.AnimationCurve.FAST_OUT_SLOW_IN)
        
        # Image URLs (local with remote fallback)
        self.image_path = decision_data.get("image", None)
        self.image_url = decision_data.get("image_url", None)
        
    def build(self):
        # Container to hold the card (allows for rotation)
        self.card_container = ft.Container(
            animate=self.animation,
            animate_rotation=self.animation,
            animate_opacity=self.animation,
            width=self.card_width,
            height=self.card_height,
            border_radius=10,
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            content=self._build_card()
        )
        
        # Container that detects gestures
        return ft.GestureDetector(
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            mouse_cursor=ft.MouseCursor.MOVE,
            content=self.card_container
        )
    
    def _build_card(self):
        """Builds the card content including image, text, and choice indicators"""
        # Image section
        image = None
        if self.image_url:
            # Try to use remote image if available
            image = ft.Image(
                src=self.image_url,
                width=self.card_width,
                height=200,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
            )
        elif self.image_path:
            # Fallback to local image
            image = ft.Image(
                src=self.image_path,
                width=self.card_width,
                height=200,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
            )
            
        # Decision text
        decision_text = ft.Text(
            value=self.decision_data.get("text", "Make a decision"),
            size=16,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        
        # Option texts
        left_option = self.decision_data.get("left", {}).get("text", "Swipe Left")
        right_option = self.decision_data.get("right", {}).get("text", "Swipe Right")
        
        left_text = ft.Text(
            value=f"← {left_option}",
            color=ft.colors.RED,
            size=14,
            weight=ft.FontWeight.BOLD,
        )
        
        right_text = ft.Text(
            value=f"{right_option} →",
            color=ft.colors.GREEN,
            size=14,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.RIGHT,
        )
        
        # Button options (alternative to swiping)
        button_row = ft.Row(
            [
                ft.ElevatedButton(
                    left_option,
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda _: self._handle_left_choice()
                ),
                ft.ElevatedButton(
                    right_option,
                    icon=ft.icons.ARROW_FORWARD,
                    icon_color=ft.colors.GREEN,
                    on_click=lambda _: self._handle_right_choice()
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Build the entire card
        content = [
            # Decision image (if available)
            image if image else ft.Container(
                width=self.card_width,
                height=200,
                bgcolor=ft.colors.BLACK12,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
                content=ft.Icon(ft.icons.IMAGE, size=40, color=ft.colors.BLACK45),
                alignment=ft.alignment.center,
            ),
            
            # Decision content
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        decision_text,
                        ft.Divider(),
                        ft.Row(
                            [left_text, right_text],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Container(height=20),  # Spacer
                        button_row,
                    ],
                    spacing=10,
                ),
            ),
        ]
        
        # Card container
        return ft.Card(
            content=ft.Column(content, tight=True),
            elevation=5,
            color=ft.colors.WHITE,
        )
    
    def _on_pan_update(self, e: ft.DragUpdateEvent):
        """Handle dragging the card left/right"""
        # Calculate horizontal drag distance
        self.drag_x = e.delta_x
        
        # Update card rotation and position
        # Limit rotation to a maximum of 15 degrees
        max_rotation = 15
        self.rotation = min(max(self.drag_x / 10, -max_rotation), max_rotation)
        
        # Update card transform
        self.card_container.rotate = ft.transform.Rotate(
            self.rotation,
            alignment=ft.alignment.center
        )
        
        # Move the card horizontally
        self.card_container.offset = ft.transform.Offset(self.drag_x / 100, 0)
        
        # Show left/right indicators based on drag direction
        if self.drag_x < -50:
            # Left swipe indicator
            self.card_container.border = ft.border.all(3, ft.colors.RED)
        elif self.drag_x > 50:
            # Right swipe indicator
            self.card_container.border = ft.border.all(3, ft.colors.GREEN)
        else:
            # No swipe yet
            self.card_container.border = None
            
        self.update()
    
    def _on_pan_end(self, e: ft.DragEndEvent):
        """Handle the end of a drag gesture"""
        # Determine if the swipe was far enough to count as a choice
        threshold = 100  # Minimum drag distance to trigger a swipe
        
        if self.drag_x < -threshold:
            # Left swipe
            self._handle_left_choice()
        elif self.drag_x > threshold:
            # Right swipe
            self._handle_right_choice()
        else:
            # Reset card position if swipe wasn't decisive
            self._reset_card()
    
    def _handle_left_choice(self):
        """Handle a left swipe choice"""
        # Animate card exit to the left
        self.card_container.offset = ft.transform.Offset(-2, 0)
        self.card_container.rotate = ft.transform.Rotate(-30, alignment=ft.alignment.center)
        self.card_container.opacity = 0
        self.update()
        
        # Call the left choice callback
        self.on_swipe_left()
    
    def _handle_right_choice(self):
        """Handle a right swipe choice"""
        # Animate card exit to the right
        self.card_container.offset = ft.transform.Offset(2, 0)
        self.card_container.rotate = ft.transform.Rotate(30, alignment=ft.alignment.center)
        self.card_container.opacity = 0
        self.update()
        
        # Call the right choice callback
        self.on_swipe_right()
    
    def _reset_card(self):
        """Reset the card to its original position"""
        self.drag_x = 0
        self.rotation = 0
        self.card_container.offset = ft.transform.Offset(0, 0)
        self.card_container.rotate = ft.transform.Rotate(0, alignment=ft.alignment.center)
        self.card_container.border = None
        self.update()