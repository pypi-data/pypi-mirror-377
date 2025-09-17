from dataclasses import dataclass
from typing import Optional
from .message import Message
from .user import User

@dataclass
class CallbackQuery:
    """Represents an incoming callback query from a callback button"""
    id: str
    from_user: User
    message: Optional[Message] = None
    data: Optional[str] = None
    chat_instance: Optional[str] = None
    game_short_name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CallbackQuery':
        """Create a CallbackQuery object from API response"""
        from_user = User.from_dict(data.get('from')) if data.get('from') else None
        message = Message.from_dict(data.get('message')) if data.get('message') else None
        
        return cls(
            id=data.get('id'),
            from_user=from_user,
            message=message,
            data=data.get('data'),
            chat_instance=data.get('chat_instance'),
            game_short_name=data.get('game_short_name')
        )
    
    async def answer(self, text: str = None, show_alert: bool = False, url: str = None, cache_time: int = None):
        """Answer this callback query"""
        # This will be implemented in the client
        pass
