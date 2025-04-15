import flet as ft
from typing import Dict, Any, Callable, Optional

def create_decision_card(
    decision_data: Dict[str, Any],
    on_swipe_left: Callable[[], None],
    on_swipe_right: Callable[[], None],
    card_width: int = 320,
    card_height: int = 420,
) -> ft.Container:
    """Create a decision card component with swipe functionality"""
    
    # Image section
    image_url = decision_data.get("image_url", None)
    image_path = decision_data.get("image", None)
    
    image = None
    if image_url:
        # Try to use remote image if available
        image = ft.Image(
            src=image_url,
            width=card_width,
            height=200,
            fit=ft.ImageFit.COVER,
        )
    elif image_path:
        # Fallback to local image
        image = ft.Image(
            src=image_path,
            width=card_width,
            height=200,
            fit=ft.ImageFit.COVER,
        )
    
    # Decision text
    decision_text = ft.Text(
        value=decision_data.get("text", "Make a decision"),
        size=16,
        weight="bold",
        text_align="center",
    )
    
    # Option texts
    left_option = decision_data.get("left", {}).get("text", "Swipe Left")
    right_option = decision_data.get("right", {}).get("text", "Swipe Right")
    
    left_text = ft.Text(
        value=f"← {left_option}",
        color="red",
        size=14,
        weight="bold",
    )
    
    right_text = ft.Text(
        value=f"{right_option} →",
        color="green",
        size=14,
        weight="bold",
        text_align="right",
    )
    
    # Button options (alternative to swiping)
    button_row = ft.Row(
        controls=[
            ft.ElevatedButton(
                text=left_option,
                icon="arrow_back",
                on_click=lambda _: on_swipe_left()
            ),
            ft.ElevatedButton(
                text=right_option,
                icon="arrow_forward",
                on_click=lambda _: on_swipe_right()
            ),
        ],
        alignment="spaceBetween",
    )
    
    # Create card content
    content = [
        # Decision image (if available)
        image if image else ft.Container(
            width=card_width,
            height=200,
            bgcolor="#E0E0E0",
            content=ft.Icon(name="image", size=40, color="#757575"),
            alignment="center",
        ),
        
        # Decision content
        ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    decision_text,
                    ft.Divider(),
                    ft.Row(
                        controls=[left_text, right_text],
                        alignment="spaceBetween",
                    ),
                    ft.Container(height=20),  # Spacer
                    button_row,
                ],
                spacing=10,
            ),
        ),
    ]
    
    # Card container
    card = ft.Card(
        content=ft.Column(controls=content, tight=True),
        elevation=5,
    )
    
    # Container for the card
    card_container = ft.Container(
        content=card,
        width=card_width,
        height=card_height,
        animate_opacity=300,
    )
    
    return card_container