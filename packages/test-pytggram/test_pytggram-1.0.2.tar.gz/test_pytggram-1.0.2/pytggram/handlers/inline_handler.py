from .handler import Handler
from ..types import InlineQuery

class InlineHandler(Handler):
    """Handler for inline query updates"""
    def __init__(self, callback, filters=None, group=0):
        super().__init__(callback, filters, group)
    
    async def handle(self, client, update: dict):
        """Handle an inline query update"""
        inline_query = InlineQuery.from_dict(update.get('inline_query', {}))
        if self.check(inline_query):
            await self.callback(client, inline_query)
