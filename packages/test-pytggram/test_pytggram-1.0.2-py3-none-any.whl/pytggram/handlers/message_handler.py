from .handler import Handler
from ..types import Message

class MessageHandler(Handler):
    """Handler for message updates"""
    def __init__(self, callback, filters=None, group=0):
        super().__init__(callback, filters, group)
    
    async def handle(self, client, update: dict):
        """Handle a message update"""
        message = Message.from_dict(update.get('message', {}))
        if self.check(message):
            await self.callback(client, message)
