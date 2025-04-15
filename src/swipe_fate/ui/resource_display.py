import flet as ft
from typing import Dict, Any, Optional, List

def create_resource_display(
    resources: Dict[str, Dict[str, Any]],
    resource_values: Dict[str, int],
    resource_icons: Optional[Dict[str, Dict[str, str]]] = None,
    width: int = 320,
) -> ft.Container:
    """Create a resource display component"""
    resource_icons = resource_icons or {}
    resource_items = []
    resource_controls = {}
    
    for resource_id, resource_info in resources.items():
        # Get current value and display name
        current_value = resource_values.get(resource_id, resource_info.get("initial", 0))
        display_name = resource_info.get("display_name", resource_id.replace("_", " ").title())
        
        # Get min/max values for progress calculation
        min_val = resource_info.get("min", 0)
        max_val = resource_info.get("max", 100)
        range_val = max_val - min_val
        
        # Calculate progress value (between 0.0 and 1.0)
        progress_val = max(0, min(1, (current_value - min_val) / range_val if range_val > 0 else 0))
        
        # Get icon if available
        icon = None
        if resource_icons and resource_id in resource_icons:
            icon_url = resource_icons[resource_id].get("url", None)
            if icon_url:
                icon = ft.Image(
                    src=icon_url,
                    width=24,
                    height=24,
                )
        
        # Create resource value text control
        value_text = ft.Text(
            value=str(current_value),
            weight="bold",
            size=16,
        )
        resource_controls[resource_id] = value_text
        
        # Create progress bar
        progress_bar = ft.ProgressBar(
            value=progress_val,
            width=100,
            color="green" if progress_val > 0.5 else "amber" if progress_val > 0.2 else "red",
            bgcolor="#E0E0E0",
        )
        
        # Create resource row
        resource_row = ft.Container(
            content=ft.Row(
                controls=[
                    # Icon or placeholder
                    icon or ft.Container(width=24, height=24),
                    # Resource name
                    ft.Text(display_name, size=14, width=120),
                    # Progress bar
                    progress_bar,
                    # Value
                    value_text,
                ],
                alignment="spaceBetween",
            ),
            padding=ft.padding.only(bottom=5, top=5),
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#E0E0E0")),
        )
        
        resource_items.append(resource_row)
    
    return ft.Container(
        width=width,
        padding=10,
        border_radius=10,
        bgcolor="white",
        border=ft.border.all(1, "#BDBDBD"),
        content=ft.Column(controls=resource_items, tight=True),
    )