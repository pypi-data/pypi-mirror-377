from dataclasses import dataclass
from typing import Optional

@dataclass
class Chat:
    """Represents a Telegram chat"""
    id: int
    type: str  # 'private', 'group', 'supergroup', 'channel'
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Chat':
        """Create a Chat object from API response"""
        return cls(
            id=data.get('id'),
            type=data.get('type'),
            title=data.get('title'),
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
    
    @property
    def is_private(self) -> bool:
        """Check if chat is private"""
        return self.type == 'private'
    
    @property
    def is_group(self) -> bool:
        """Check if chat is a group"""
        return self.type in ['group', 'supergroup']
    
    @property
    def is_channel(self) -> bool:
        """Check if chat is a channel"""
        return self.type == 'channel'
