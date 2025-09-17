from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from .user import User
from .chat import Chat

@dataclass
class Message:
    """Represents a Telegram message"""
    message_id: int
    from_user: Optional[User] = None
    chat: Optional[Chat] = None
    text: Optional[str] = None
    date: Optional[int] = None
    reply_to_message: Optional['Message'] = None
    entities: Optional[List[Dict[str, Any]]] = None
    caption: Optional[str] = None
    media_type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create a Message object from API response"""
        from_user = User.from_dict(data.get('from')) if data.get('from') else None
        chat = Chat.from_dict(data.get('chat')) if data.get('chat') else None
        reply_to_message = cls.from_dict(data.get('reply_to_message')) if data.get('reply_to_message') else None
        
        # Determine media type
        media_type = None
        if data.get('photo'):
            media_type = 'photo'
        elif data.get('document'):
            media_type = 'document'
        elif data.get('video'):
            media_type = 'video'
        elif data.get('audio'):
            media_type = 'audio'
        elif data.get('voice'):
            media_type = 'voice'
        elif data.get('sticker'):
            media_type = 'sticker'
        elif data.get('location'):
            media_type = 'location'
        elif data.get('contact'):
            media_type = 'contact'
        elif data.get('poll'):
            media_type = 'poll'
        
        return cls(
            message_id=data.get('message_id'),
            from_user=from_user,
            chat=chat,
            text=data.get('text'),
            date=data.get('date'),
            reply_to_message=reply_to_message,
            entities=data.get('entities'),
            caption=data.get('caption'),
            media_type=media_type
        )
    
    def reply(self, text: str, **kwargs) -> 'Message':
        """Reply to this message"""
        # This will be implemented in the client
        pass
    
    @property
    def is_command(self) -> bool:
        """Check if message is a command"""
        return self.text and self.text.startswith('/')
    
    @property
    def command(self) -> Optional[str]:
        """Get command from message"""
        if self.is_command and self.entities:
            for entity in self.entities:
                if entity.get('type') == 'bot_command':
                    command_text = self.text[entity.get('offset'):entity.get('offset') + entity.get('length')]
                    return command_text.split('@')[0]  # Remove bot username if present
        return None
    
    @property
    def command_args(self) -> Optional[str]:
        """Get command arguments"""
        if self.is_command and self.entities:
            for entity in self.entities:
                if entity.get('type') == 'bot_command':
                    return self.text[entity.get('offset') + entity.get('length'):].strip()
        return None
