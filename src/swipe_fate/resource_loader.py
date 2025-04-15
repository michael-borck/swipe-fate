import json
from typing import Dict, List, Any, Optional

class ResourceLoader:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.data = self.load_json()

    def load_json(self) -> Dict[str, Any]:
        """Load and parse the JSON file."""
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            print("JSON data loaded successfully.")
            return data
        except FileNotFoundError:
            print("File not found.")
            return {}
        except json.JSONDecodeError:
            print("Error decoding JSON.")
            return {}
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