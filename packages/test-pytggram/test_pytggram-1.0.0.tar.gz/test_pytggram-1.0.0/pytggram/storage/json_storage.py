import json
import os
from typing import Any, Optional

class JSONStorage:
    """JSON file-based storage for bot data"""
    def __init__(self, filename='bot_data.json'):
        self.filename = filename
        self.data = self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
        self._save_data()
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self._save_data()
    
    def clear(self):
        self.data = {}
        self._save_data()
    
    def keys(self):
        return list(self.data.keys())
