from .handler import Handler
from ..types import Poll, PollAnswer

class PollHandler(Handler):
    """Handler for poll updates"""
    def __init__(self, callback, filters=None, group=0):
        super().__init__(callback, filters, group)
    
    async def handle(self, client, update: dict):
        """Handle a poll update"""
        if 'poll' in update:
            poll = Poll.from_dict(update.get('poll', {}))
            if self.check(poll):
                await self.callback(client, poll)
        elif 'poll_answer' in update:
            poll_answer = PollAnswer.from_dict(update.get('poll_answer', {}))
            if self.check(poll_answer):
                await self.callback(client, poll_answer)
