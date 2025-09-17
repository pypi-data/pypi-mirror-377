from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId

class PyTgGramBaseModel:
    """Base model for all MongoDB documents"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        data = self.__dict__.copy()
        data.pop('_id', None)  # Remove MongoDB _id field
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model from dictionary"""
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

class User(PyTgGramBaseModel):
    """User model for MongoDB"""
    
    def __init__(self, user_id: int, is_bot: bool, first_name: str, 
                 last_name: Optional[str] = None, username: Optional[str] = None,
                 language_code: Optional[str] = None, created_at: datetime = None):
        self._id = None
        self.user_id = user_id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

class Chat(PyTgGramBaseModel):
    """Chat model for MongoDB"""
    
    def __init__(self, chat_id: int, type: str, title: Optional[str] = None,
                 username: Optional[str] = None, first_name: Optional[str] = None,
                 last_name: Optional[str] = None, created_at: datetime = None):
        self._id = None
        self.chat_id = chat_id
        self.type = type  # 'private', 'group', 'supergroup', 'channel'
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = datetime.utcnow()

class Message(PyTgGramBaseModel):
    """Message model for MongoDB"""
    
    def __init__(self, message_id: int, chat_id: int, user_id: int, text: Optional[str] = None,
                 reply_to_message_id: Optional[int] = None, date: datetime = None,
                 media_type: Optional[str] = None, media_data: Optional[Dict] = None):
        self._id = None
        self.message_id = message_id
        self.chat_id = chat_id
        self.user_id = user_id
        self.text = text
        self.reply_to_message_id = reply_to_message_id
        self.date = date or datetime.utcnow()
        self.media_type = media_type  # 'photo', 'document', 'video', etc.
        self.media_data = media_data or {}
        self.created_at = datetime.utcnow()

class UserData(PyTgGramBaseModel):
    """User data model for key-value storage"""
    
    def __init__(self, user_id: int, key: str, value: Any, created_at: datetime = None):
        self._id = None
        self.user_id = user_id
        self.key = key
        self.value = value
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = datetime.utcnow()

class ChatData(PyTgGramBaseModel):
    """Chat data model for key-value storage"""
    
    def __init__(self, chat_id: int, key: str, value: Any, created_at: datetime = None):
        self._id = None
        self.chat_id = chat_id
        self.key = key
        self.value = value
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = datetime.utcnow()
