import json
from typing import Dict, List, Any, Optional

class ResourceLoader:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.data = self.load_json()

    def load_json(self) -> Dict[str, Any]:
        """Load and parse the JSON file."""
        try:
            # First read the file
            with open(self.file_path, 'r') as file:
                file_content = file.read()
            
            # Pre-process to handle the + and - signs in effects
            # Replace +10 with 10 and -5 with -5
            import re
            preprocessed_content = re.sub(r'(\s+)"(\w+)":\s*\+(\d+)', r'\1"\2": \3', file_content)
            
            # Load the preprocessed content
            data = json.loads(preprocessed_content)
            print(f"JSON data loaded successfully from {self.file_path}")
            return data
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            # Return a basic structure for debugging
            return {
                "metadata": {"name": "Debug Game"},
                "resources": {"debug": {"initial": 100, "min": 0, "max": 100, "display_name": "Debug"}},
                "decisions": [
                    {
                        "id": "debug",
                        "text": "JSON loading error. Please check file format.",
                        "left": {"text": "OK", "effects": {}, "next": "debug"},
                        "right": {"text": "OK", "effects": {}, "next": "debug"}
                    }
                ]
            }
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}

    def get_decisions(self) -> List[Dict[str, Any]]:
        """Retrieve all decision cards from the data."""
        return self.data.get('decisions', [])

    def get_rules(self) -> List[Dict[str, Any]]:
        """Retrieve all rules from the data."""
        return self.data.get('rules', [])

    def get_events(self) -> List[Dict[str, Any]]:
        """Retrieve all events from the data."""
        return self.data.get('events', [])

    def get_resources(self) -> Dict[str, Any]:
        """Retrieve the initial resource states from the data."""
        return self.data.get('resources', {})

    def get_themes(self) -> Dict[str, Any]:
        """Retrieve all themes from the data."""
        return self.data.get('themes', {})