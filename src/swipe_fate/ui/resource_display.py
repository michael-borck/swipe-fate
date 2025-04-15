import flet as ft
from typing import Dict, Any, Optional, List

class ResourceDisplay(ft.UserControl):
    def __init__(
        self,
        resources: Dict[str, Dict[str, Any]],
        resource_values: Dict[str, int],
        resource_icons: Optional[Dict[str, Dict[str, str]]] = None,
        width: int = 320,
    ):
        super().__init__()
        self.resources = resources
        self.resource_values = resource_values
        self.resource_icons = resource_icons or {}
        self.width = width
        self.resource_controls: Dict[str, ft.Text] = {}
        self.animation = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
        
    def build(self):
        resource_items = []
        
        for resource_id, resource_info in self.resources.items():
            # Get current value and display name
            current_value = self.resource_values.get(resource_id, resource_info.get("initial", 0))
            display_name = resource_info.get("display_name", resource_id.replace("_", " ").title())
            
            # Get min/max values for progress calculation
            min_val = resource_info.get("min", 0)
            max_val = resource_info.get("max", 100)
            range_val = max_val - min_val
            
            # Calculate progress value (between 0.0 and 1.0)
            progress_val = max(0, min(1, (current_value - min_val) / range_val if range_val > 0 else 0))
            
            # Get icon if available
            icon = None
            if self.resource_icons and resource_id in self.resource_icons:
                icon_url = self.resource_icons[resource_id].get("url", None)
                if icon_url:
                    icon = ft.Image(
                        src=icon_url,
                        width=24,
                        height=24,
                    )
            
            # Create resource value text control
            value_text = ft.Text(
                value=str(current_value),
                weight=ft.FontWeight.BOLD,
                size=16,
            )
            self.resource_controls[resource_id] = value_text
            
            # Create progress bar
            progress_bar = ft.ProgressBar(
                value=progress_val,
                width=100,
                color="green" if progress_val > 0.5 else "amber" if progress_val > 0.2 else "red",
                bgcolor=ft.colors.BLACK12,
            )
            
            # Create resource row
            resource_row = ft.Container(
                content=ft.Row(
                    [
                        # Icon or placeholder
                        icon or ft.Container(width=24, height=24),
                        # Resource name
                        ft.Text(display_name, size=14, width=120),
                        # Progress bar
                        progress_bar,
                        # Value
                        value_text,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.only(bottom=5, top=5),
                border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.BLACK12)),
            )
            
            resource_items.append(resource_row)
        
        return ft.Container(
            width=self.width,
            padding=10,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.BLACK26),
            animate=self.animation,
            content=ft.Column(resource_items, tight=True),
        )
    
    def update_resources(self, new_values: Dict[str, int], highlight_changes: bool = True):
        """Update resource values and highlight changes"""
        changes = []
        
        for resource_id, new_value in new_values.items():
            if resource_id in self.resource_controls:
                old_value = self.resource_values.get(resource_id, 0)
                self.resource_values[resource_id] = new_value
                
                # Update the display text
                self.resource_controls[resource_id].value = str(new_value)
                
                # Highlight changes
                if highlight_changes and new_value != old_value:
                    if new_value > old_value:
                        self.resource_controls[resource_id].color = ft.colors.GREEN
                    elif new_value < old_value:
                        self.resource_controls[resource_id].color = ft.colors.RED
                    
                    # Add to list of controls to animate
                    changes.append(self.resource_controls[resource_id])
                    
                    # Reset color after a delay (creates a flash effect)
                    def reset_color(control):
                        control.color = None
                        self.update()
                    
                    self.page.after(1000, lambda c=self.resource_controls[resource_id]: reset_color(c))
        
        self.update()