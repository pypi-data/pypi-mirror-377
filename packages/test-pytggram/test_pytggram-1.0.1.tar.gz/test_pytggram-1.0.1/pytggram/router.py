from typing import Dict, Callable, Any, List
from .utils import setup_logger
from .filters import Filter

class Router:
    """Advanced router for handling different types of updates with filters"""
    
    def __init__(self):
        self.logger = setup_logger('pytggram.router')
        self.message_handlers: List[Dict[str, Any]] = []
        self.callback_handlers: List[Dict[str, Any]] = []
        self.inline_handlers: List[Dict[str, Any]] = []
        self.poll_handlers: List[Dict[str, Any]] = []
    
    def add_message_handler(self, handler: Callable, filters: Filter = None):
        """Add a message handler"""
        self.message_handlers.append({
            'handler': handler,
            'filters': filters
        })
    
    def add_callback_handler(self, handler: Callable, filters: Filter = None):
        """Add a callback handler"""
        self.callback_handlers.append({
            'handler': handler,
            'filters': filters
        })
    
    def add_inline_handler(self, handler: Callable, filters: Filter = None):
        """Add an inline handler"""
        self.inline_handlers.append({
            'handler': handler,
            'filters': filters
        })
    
    def add_poll_handler(self, handler: Callable, filters: Filter = None):
        """Add a poll handler"""
        self.poll_handlers.append({
            'handler': handler,
            'filters': filters
        })
    
    async def route_message(self, message):
        """Route a message to the appropriate handler"""
        for handler_info in self.message_handlers:
            if handler_info['filters'] is None or handler_info['filters'](message):
                try:
                    await handler_info['handler'](message)
                    break  # Stop after first matching handler
                except Exception as e:
                    self.logger.error(f"Error in message handler: {e}")
    
    async def route_callback(self, callback_query):
        """Route a callback query to the appropriate handler"""
        for handler_info in self.callback_handlers:
            if handler_info['filters'] is None or handler_info['filters'](callback_query):
                try:
                    await handler_info['handler'](callback_query)
                    break  # Stop after first matching handler
                except Exception as e:
                    self.logger.error(f"Error in callback handler: {e}")
    
    async def route_inline(self, inline_query):
        """Route an inline query to the appropriate handler"""
        for handler_info in self.inline_handlers:
            if handler_info['filters'] is None or handler_info['filters'](inline_query):
                try:
                    await handler_info['handler'](inline_query)
                    break  # Stop after first matching handler
                except Exception as e:
                    self.logger.error(f"Error in inline handler: {e}")
    
    async def route_poll(self, poll):
        """Route a poll to the appropriate handler"""
        for handler_info in self.poll_handlers:
            if handler_info['filters'] is None or handler_info['filters'](poll):
                try:
                    await handler_info['handler'](poll)
                    break  # Stop after first matching handler
                except Exception as e:
                    self.logger.error(f"Error in poll handler: {e}")
