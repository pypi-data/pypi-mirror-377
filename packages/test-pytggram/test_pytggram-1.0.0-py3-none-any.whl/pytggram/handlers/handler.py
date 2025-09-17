from typing import Callable, Any
from ..filters import Filter

class Handler:
    """Base class for all handlers"""
    def __init__(self, callback: Callable, filters: Filter = None, group: int = 0):
        self.callback = callback
        self.filters = filters
        self.group = group
    
    def check(self, update: Any) -> bool:
        """Check if this handler should handle the update"""
        if self.filters:
            return self.filters(update)
        return True
    
    async def handle(self, client, update: dict):
        """Handle an update"""
        raise NotImplementedError("Handler subclasses must implement handle() method")
