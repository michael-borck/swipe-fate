from typing import Any, Callable, Optional

import flet as ft

from swipe_verse.models.card import Card


# Note: For Flet 0.27.x compatibility, we extend GestureDetector instead of UserControl
class CardDisplay(ft.GestureDetector):
    def __init__(
        self,
        card: Card,
        on_swipe_left: Optional[Callable[[ft.DragEndEvent], None]] = None,
        on_swipe_right: Optional[Callable[[ft.DragEndEvent], None]] = None,
        **kwargs: Any,
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
        self.choice_overlay_stack: Optional[ft.Stack] = None  # Renamed for clarity
        self.left_choice_text: Optional[ft.Text] = None  # Text for left choice
        self.right_choice_text: Optional[ft.Text] = None # Text for right choice

        super().__init__(
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            **kwargs,
        )

    def build(self) -> ft.Container:
        # Responsive sizing
        page_width = 300
        if self.page and hasattr(self.page, "width") and self.page.width is not None:
            page_width = self.page.width

        container_width = min(350, page_width * 0.8)
        container_height = container_width * 1.5  # 3:2 aspect ratio

        # Calculate inner content dimensions
        image_width = container_width * 0.85  # Leave space for borders
        image_height = image_width * 0.8  # 250x200 aspect ratio for artwork
        title_height = container_height * 0.1
        text_height = container_height * 0.25

        # Card title
        card_title = ft.Container(
            content=ft.Text(
                self.card.title,
                size=18,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                color=ft.colors.BLACK,
                max_lines=2, # Prevent overflow
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            width=image_width,
            height=title_height,
            alignment=ft.alignment.center,
            padding=ft.padding.only(top=10),
        )

        # Card image
        image_path = getattr(self.card, 'image', None)
        if not isinstance(image_path, str) or not image_path:
            print(f"Warning: Card {self.card.id} has invalid or missing image path: {image_path}. Using default.")
            image_path = "assets/default/card_fronts/event.png"

        self.card_image = ft.Image(
            src=image_path,
            width=image_width,
            height=image_height,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Text("Image?"), # Simpler error
        )

        # Card text
        card_text = ft.Container(
            content=ft.Text(
                self.card.text,
                size=14,
                text_align=ft.TextAlign.CENTER,
                color=ft.colors.BLACK,
                max_lines=3,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            width=image_width,
            height=text_height,
            padding=ft.padding.all(8),
            alignment=ft.alignment.center,
        )

        # Combine all elements in a column
        card_content = ft.Column(
            controls=[
                card_title,
                self.card_image,
                card_text,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )

        # The card container
        self.card_container = ft.Container(
            content=card_content,
            width=container_width,
            height=container_height,
            border_radius=ft.border_radius.all(10),
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.BLACK26,
                offset=ft.Offset(2, 2),
            ),
            border=ft.border.all(1, ft.colors.BLACK12),
            animate_offset=ft.animation.Animation(100, ft.AnimationCurve.EASE_OUT),
            animate_rotation=ft.animation.Animation(100, ft.AnimationCurve.EASE_OUT),
            padding=ft.padding.only(top=5, bottom=5),
        )

        # --- Overlay Elements --- 
        # Positioned within the Stack, drawn *after* the card_container
        self.left_choice_text = ft.Text(
            self.card.choices.left.text if self.card.choices and self.card.choices.left else "",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.with_opacity(0.9, ft.colors.WHITE),
            bgcolor=ft.colors.with_opacity(0.7, ft.colors.RED_ACCENT_700),
            padding=10,
            border_radius=5,
            rotate=ft.transform.Rotate(-0.15),
            # Use alignment within Stack instead of offset
            # offset=ft.transform.Offset(-0.15, 0.15),
            visible=False,
            opacity=0,
            animate_opacity=ft.animation.Animation(100, ft.AnimationCurve.LINEAR),
        )
        self.right_choice_text = ft.Text(
            self.card.choices.right.text if self.card.choices and self.card.choices.right else "",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.with_opacity(0.9, ft.colors.WHITE),
            bgcolor=ft.colors.with_opacity(0.7, ft.colors.GREEN_700),
            padding=10,
            border_radius=5,
            rotate=ft.transform.Rotate(0.15),
            # Use alignment within Stack instead of offset
            # offset=ft.transform.Offset(0.15, 0.15),
            visible=False,
            opacity=0,
            animate_opacity=ft.animation.Animation(100, ft.AnimationCurve.LINEAR),
        )

        # --- Stack Layout --- 
        # Holds the card and the overlays
        self.choice_overlay_stack = ft.Stack(
            [
                self.card_container, # Base layer
                # Align overlays within the Stack
                ft.Container(
                    self.left_choice_text,
                    alignment=ft.alignment.top_left,
                    margin=ft.margin.only(top=20, left=20) # Adjust positioning
                ),
                ft.Container(
                    self.right_choice_text,
                    alignment=ft.alignment.top_right,
                    margin=ft.margin.only(top=20, right=20) # Adjust positioning
                ),
            ]
        )

        # --- Final GestureDetector Container --- 
        # This is what the GestureDetector itself returns
        # It contains the Stack
        return ft.Container(
            content=self.choice_overlay_stack,
            width=container_width,
            height=container_height,
            alignment=ft.alignment.center,
            # clip_behavior=ft.ClipBehavior.NONE, # Removing clip behavior, let Stack manage children
        )

    def _on_pan_start(self, e: ft.DragStartEvent) -> None:
        self.is_swiping = True
        self.start_x = e.local_x
        self.current_x = e.local_x

    def _on_pan_update(self, e: ft.DragUpdateEvent) -> None:
        if not self.is_swiping or not self.card_container or not self.left_choice_text or not self.right_choice_text:
            return

        self.current_x = e.local_x
        delta_x = self.current_x - self.start_x

        # Card Movement (relative to the container width)
        container_width = self.card_container.width or 1 # Avoid division by zero
        self.card_container.offset = ft.transform.Offset(delta_x / container_width, 0)

        # Rotation
        angle = (delta_x / (self.swipe_threshold * 1.5)) * 0.3
        self.card_container.rotate = ft.transform.Rotate(angle)

        # Overlay Visibility & Opacity
        overlay_threshold = 15
        intensity = max(0.0, min(1.0, (abs(delta_x) - overlay_threshold) / (self.swipe_threshold - overlay_threshold)))

        if delta_x > overlay_threshold:
            self.right_choice_text.visible = True
            self.right_choice_text.opacity = intensity
            self.left_choice_text.visible = False
            self.left_choice_text.opacity = 0
        elif delta_x < -overlay_threshold:
            self.left_choice_text.visible = True
            self.left_choice_text.opacity = intensity
            self.right_choice_text.visible = False
            self.right_choice_text.opacity = 0
        else:
            self.left_choice_text.visible = False
            self.left_choice_text.opacity = 0
            self.right_choice_text.visible = False
            self.right_choice_text.opacity = 0

        self.update()

    def _on_pan_end(self, e: ft.DragEndEvent) -> None:
        if not self.is_swiping or not self.card_container or not self.left_choice_text or not self.right_choice_text:
            return

        self.is_swiping = False
        delta_x = self.current_x - self.start_x

        # Reset card appearance
        self.card_container.offset = ft.transform.Offset(0, 0)
        self.card_container.rotate = ft.transform.Rotate(0)

        # Hide overlays
        self.left_choice_text.visible = False
        self.left_choice_text.opacity = 0
        self.right_choice_text.visible = False
        self.right_choice_text.opacity = 0

        self.update() # Update UI immediately

        # Trigger swipe action if threshold met
        if abs(delta_x) > self.swipe_threshold:
            if delta_x > 0 and self.on_swipe_right:
                self.on_swipe_right(e)
            elif delta_x < 0 and self.on_swipe_left:
                self.on_swipe_left(e)

    def update_card(self, card: Card) -> None:
        self.card = card

        if not all([self.card_container, self.left_choice_text, self.right_choice_text]):
            print("Error: CardDisplay UI elements not fully initialized during update_card")
            return

        # Update card content directly (more robust)
        # Assuming self.card_container.content is the ft.Column
        if isinstance(self.card_container.content, ft.Column) and len(self.card_container.content.controls) == 3:
            title_container = self.card_container.content.controls[0]
            image_control = self.card_container.content.controls[1]
            text_container = self.card_container.content.controls[2]

            if isinstance(title_container, ft.Container) and isinstance(title_container.content, ft.Text):
                title_container.content.value = card.title

            if isinstance(image_control, ft.Image):
                image_path = getattr(card, 'image', None)
                if not isinstance(image_path, str) or not image_path:
                    image_path = "assets/default/card_fronts/event.png"
                image_control.src = image_path

            if isinstance(text_container, ft.Container) and isinstance(text_container.content, ft.Text):
                text_container.content.value = card.text
        else:
            print("Error: Could not update card content structure.")

        # Update overlay text values
        self.left_choice_text.value = card.choices.left.text if card.choices and card.choices.left else ""
        self.right_choice_text.value = card.choices.right.text if card.choices and card.choices.right else ""

        # Reset visual state
        self.card_container.offset = ft.transform.Offset(0, 0)
        self.card_container.rotate = ft.transform.Rotate(0)
        self.left_choice_text.visible = False
        self.left_choice_text.opacity = 0
        self.right_choice_text.visible = False
        self.right_choice_text.opacity = 0

        self.update()
