import os
import sys
import json
import tempfile
import pytest
from pytest import MonkeyPatch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from swipe_fate.resource_loader import ResourceLoader

class TestResourceLoader:
    def test_load_json_success(self):
        # Create a temporary JSON file
        test_data = {"key": "value"}
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            # Test loading the file
            loader = ResourceLoader(temp_file)
            assert loader.data == test_data
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_get_decisions(self, monkeypatch):
        test_data = {"decisions": [{"id": 1}, {"id": 2}]}
        
        # Mock the open function
        mock_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        json.dump(test_data, mock_file)
        mock_file.close()
        
        try:
            # Create loader with mocked file
            loader = ResourceLoader(mock_file.name)
            assert loader.get_decisions() == test_data["decisions"]
        finally:
            os.unlink(mock_file.name)
    
    def test_file_not_found(self):
        loader = ResourceLoader("nonexistent_file.json")
        assert loader.data == {}