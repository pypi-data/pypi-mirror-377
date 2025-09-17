from .handler import Handler
from ..types import CallbackQuery

class CallbackHandler(Handler):
    """Handler for callback query updates"""
    def __init__(self, callback, filters=None, group=0):
        super().__init__(callback, filters, group)
    
    async def handle(self, client, update: dict):
        """Handle a callback query update"""
        callback_query = CallbackQuery.from_dict(update.get('callback_query', {}))
        if self.check(callback_query):
            await self.callback(client, callback_query)
