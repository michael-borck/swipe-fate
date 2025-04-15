"""
Modern swipeable card component for SwipeFate
"""
import flet as ft
from typing import Callable, Dict, Any, Optional

class SwipeCard(ft.Control):
    """A card that can be swiped left or right to make decisions"""
    
    def __init__(
        self,
        card_data: Dict[str, Any],
        on_swipe_left: Callable[[], None],
        on_swipe_right: Callable[[], None],
        width: int = 350,
        height: int = 450,
    ):
        super().__init__()
        self.card_data = card_data
        self.on_swipe_left = on_swipe_left
        self.on_swipe_right = on_swipe_right
        self.width = width
        self.height = height
        
        # Swipe state
        self.start_x = 0
        self.current_x = 0
        self.swipe_threshold = 100  # Minimum distance to trigger a swipe
        
        # Animation settings
        self.animation_duration = 300
        self.animation = ft.animation.Animation(
            duration=self.animation_duration,
            curve=ft.animation.AnimationCurve.EASE_OUT
        )
        
        # Create the content now instead of in build()
        self._create_content()
    
    def _create_content(self):
        """Create the card content"""
        # Extract card data
        decision_text = self.card_data.get("text", "Make a decision")
        left_option = self.card_data.get("left", {}).get("text", "Left option")
        right_option = self.card_data.get("right", {}).get("text", "Right option")
        image_url = self.card_data.get("image_url", None)
        
        # Build card content
        card_content = []
        
        # Card image if available
        if image_url:
            card_content.append(
                ft.Image(
                    src=image_url,
                    width=self.width,
                    height=200,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.only(top_left=10, top_right=10),
                )
            )
        
        # Decision text
        card_content.append(
            ft.Container(
                content=ft.Text(
                    value=decision_text,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=15,
                margin=ft.margin.only(top=15, bottom=5),
            )
        )
        
        # Options (left and right)
        option_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        value="← " + left_option,
                        size=14,
                        color=ft.colors.RED,
                        text_align=ft.TextAlign.LEFT,
                    ),
                    margin=10,
                    width=self.width / 2 - 20,
                ),
                ft.Container(
                    content=ft.Text(
                        value=right_option + " →",
                        size=14,
                        color=ft.colors.GREEN,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    margin=10,
                    width=self.width / 2 - 20,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        card_content.append(option_row)
        
        # Create help text
        help_text = ft.Text(
            value="Swipe left or right to decide",
            size=12,
            color=ft.colors.GREY_500,
            italic=True,
            text_align=ft.TextAlign.CENTER,
        )
        card_content.append(
            ft.Container(
                content=help_text,
                margin=ft.margin.only(top=10, bottom=5),
            )
        )
        
        # Create the card
        self.card = ft.Card(
            content=ft.Column(
                controls=card_content,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=self.width,
            height=self.height,
            elevation=5,
        )
        
        # Wrap the card in a container for animations and transforms
        self.card_container = ft.Container(
            content=self.card,
            width=self.width,
            height=self.height,
            animate=self.animation,
            offset=ft.transform.Offset(0, 0),
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
            opacity=1.0,
        )
        
        # Create indicators for swipe direction
        self.left_indicator = ft.Container(
            width=60,
            height=60,
            border_radius=30,
            bgcolor=ft.colors.RED_100,
            opacity=0,
            animate_opacity=self.animation,
            content=ft.Icon(ft.icons.CLOSE, color=ft.colors.RED, size=30),
            alignment=ft.alignment.center,
            left=10,
            top=10,
        )
        
        self.right_indicator = ft.Container(
            width=60,
            height=60,
            border_radius=30,
            bgcolor=ft.colors.GREEN_100,
            opacity=0,
            animate_opacity=self.animation,
            content=ft.Icon(ft.icons.CHECK, color=ft.colors.GREEN, size=30),
            alignment=ft.alignment.center,
            right=10,
            top=10,
        )
        
        # Stack containing card and indicators
        self.stack = ft.Stack(
            controls=[
                self.card_container,
                self.left_indicator,
                self.right_indicator,
            ],
            width=self.width,
            height=self.height,
        )
        
        # Wrap everything in a gesture detector
        self.gesture_detector = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.MOVE,
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            content=self.stack,
        )
        
        # Set as the main content
        self.content = self.gesture_detector
    
    def _on_pan_start(self, e: ft.DragStartEvent):
        """Handle the start of a drag gesture"""
        self.start_x = e.local_x
        self.current_x = e.local_x
    
    def _on_pan_update(self, e: ft.DragUpdateEvent):
        """Handle drag updates during a swipe"""
        # Calculate the drag distance
        self.current_x = e.local_x
        drag_distance = self.current_x - self.start_x
        
        # Calculate rotation based on drag (max 15 degrees)
        rotation = min(max(drag_distance / 20, -15), 15)
        
        # Update card position and rotation
        self.card_container.offset = ft.transform.Offset(drag_distance / 100, 0)
        self.card_container.rotate = ft.transform.Rotate(
            rotation, alignment=ft.alignment.center
        )
        
        # Update indicators
        if drag_distance < -50:  # Dragging left
            self.left_indicator.opacity = min(1.0, abs(drag_distance) / 200)
            self.right_indicator.opacity = 0
        elif drag_distance > 50:  # Dragging right
            self.right_indicator.opacity = min(1.0, abs(drag_distance) / 200)
            self.left_indicator.opacity = 0
        else:  # Not dragging enough in either direction
            self.left_indicator.opacity = 0
            self.right_indicator.opacity = 0
        
        self.update()
    
    def _on_pan_end(self, e: ft.DragEndEvent):
        """Handle the end of a drag gesture"""
        drag_distance = self.current_x - self.start_x
        
        # Check if the drag distance exceeds the threshold
        if drag_distance < -self.swipe_threshold:  # Swiped left
            self._handle_swipe_left()
        elif drag_distance > self.swipe_threshold:  # Swiped right
            self._handle_swipe_right()
        else:  # Not swiped far enough, reset the card
            self._reset_card()
    
    def _handle_swipe_left(self):
        """Handle a swipe to the left"""
        # Animate card exiting to the left
        self.card_container.offset = ft.transform.Offset(-2, 0)
        self.card_container.rotate = ft.transform.Rotate(-15, alignment=ft.alignment.center)
        self.card_container.opacity = 0
        self.left_indicator.opacity = 1.0
        self.update()
        
        # Call the swipe left callback
        if self.on_swipe_left:
            self.on_swipe_left()
    
    def _handle_swipe_right(self):
        """Handle a swipe to the right"""
        # Animate card exiting to the right
        self.card_container.offset = ft.transform.Offset(2, 0)
        self.card_container.rotate = ft.transform.Rotate(15, alignment=ft.alignment.center)
        self.card_container.opacity = 0
        self.right_indicator.opacity = 1.0
        self.update()
        
        # Call the swipe right callback
        if self.on_swipe_right:
            self.on_swipe_right()
    
    def _reset_card(self):
        """Reset the card to its original position"""
        self.card_container.offset = ft.transform.Offset(0, 0)
        self.card_container.rotate = ft.transform.Rotate(0, alignment=ft.alignment.center)
        self.left_indicator.opacity = 0
        self.right_indicator.opacity = 0
        self.update()
    
    def add_button_controls(self):
        """Add manual button controls below the card for non-touch devices"""
        button_row = ft.Row(
            controls=[
                ft.ElevatedButton(
                    text="← " + self.card_data.get("left", {}).get("text", "Left"),
                    on_click=lambda _: self._handle_swipe_left(),
                    bgcolor=ft.colors.RED,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    text=self.card_data.get("right", {}).get("text", "Right") + " →",
                    on_click=lambda _: self._handle_swipe_right(),
                    bgcolor=ft.colors.GREEN,
                    color=ft.colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=self.width,
        )
        
        return button_row