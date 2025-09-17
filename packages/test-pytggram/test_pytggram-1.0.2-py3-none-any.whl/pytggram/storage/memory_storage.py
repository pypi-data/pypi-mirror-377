from typing import Any, Optional

class MemoryStorage:
    """Simple in-memory storage for bot data"""
    def __init__(self):
        self.data = {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
    
    def clear(self):
        self.data.clear()
    
    def keys(self):
        return list(self.data.keys())
    
    def values(self):
        return list(self.data.values())
    
    def items(self):
        return list(self.data.items())
