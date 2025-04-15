import flet as ft

def main(page: ft.Page):
    """Main entry point for the application"""
    print("Starting minimal working example")
    
    # Configure default page settings
    page.title = "Minimal SwipeFate"
    page.bgcolor = "white"
    page.padding = 20
    
    # Add a header
    header = ft.Text(value="SwipeFate - Minimal Version", size=30, color="red")
    page.add(header)
    
    # Create a simple card
    def handle_button_click(e):
        print(f"Button clicked: {e.control.text}")
        page.controls = [
            header,
            ft.Text(value=f"You clicked: {e.control.text}", size=20, color="blue")
        ]
        page.update()
    
    button1 = ft.ElevatedButton(text="Business Simulator", on_click=handle_button_click, bgcolor="blue", color="white")
    button2 = ft.ElevatedButton(text="Space Explorer", on_click=handle_button_click, bgcolor="purple", color="white")
    
    # Add to page
    page.add(ft.Text(value="Choose a game:", size=20))
    page.add(button1)
    page.add(button2)
    
    # Print some debug info
    print(f"Total controls: {len(page.controls)}")
    for i, control in enumerate(page.controls):
        print(f"Control {i}: {type(control).__name__}")
    
    print("Minimal page setup complete")

if __name__ == "__main__":
    ft.app(target=main)