import asyncio
from typing import Dict, Any, List
from .handlers import Handler, MessageHandler, CallbackHandler, InlineHandler, PollHandler
from .utils import setup_logger

class Dispatcher:
    """Advanced dispatcher for handling updates with priority groups"""
    
    def __init__(self):
        self.logger = setup_logger('pytggram.dispatcher')
        self.handlers: List[Handler] = []
        self.handler_groups: Dict[int, List[Handler]] = {}
    
    def add_handler(self, handler: Handler, group: int = 0):
        """Add a handler with group priority"""
        if group not in self.handler_groups:
            self.handler_groups[group] = []
        
        self.handler_groups[group].append(handler)
        self.handlers.append(handler)
        self.logger.debug(f"Added handler {handler.__class__.__name__} to group {group}")
    
    def remove_handler(self, handler: Handler):
        """Remove a handler"""
        for group in self.handler_groups.values():
            if handler in group:
                group.remove(handler)
        
        if handler in self.handlers:
            self.handlers.remove(handler)
    
    async def process_update(self, client, update: Dict[str, Any]):
        """Process an update through all handlers in order of group priority"""
        handled = False
        
        # Get sorted groups (lower numbers have higher priority)
        sorted_groups = sorted(self.handler_groups.keys())
        
        for group in sorted_groups:
            for handler in self.handler_groups[group]:
                try:
                    if 'message' in update and isinstance(handler, MessageHandler):
                        await handler.handle(client, update)
                        handled = True
                    elif 'callback_query' in update and isinstance(handler, CallbackHandler):
                        await handler.handle(client, update)
                        handled = True
                    elif 'inline_query' in update and isinstance(handler, InlineHandler):
                        await handler.handle(client, update)
                        handled = True
                    elif 'poll' in update and isinstance(handler, PollHandler):
                        await handler.handle(client, update)
                        handled = True
                except Exception as e:
                    self.logger.error(f"Error in handler {handler}: {e}")
        
        if not handled:
            self.logger.debug(f"No handler found for update: {update}")
