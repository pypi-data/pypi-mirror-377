from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """Represents a Telegram user"""
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create a User object from API response"""
        return cls(
            id=data.get('id'),
            is_bot=data.get('is_bot', False),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            username=data.get('username'),
            language_code=data.get('language_code')
        )
    
    @property
    def full_name(self) -> str:
        """Get the user's full name"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def mention(self) -> str:
        """Get user mention"""
        if self.username:
            return f"@{self.username}"
        return self.full_name
