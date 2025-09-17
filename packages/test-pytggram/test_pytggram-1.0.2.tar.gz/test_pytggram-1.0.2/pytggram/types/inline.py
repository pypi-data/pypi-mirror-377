from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from .user import User

@dataclass
class InlineQuery:
    """Represents an incoming inline query"""
    id: str
    from_user: User
    query: str
    offset: str
    chat_type: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InlineQuery':
        """Create an InlineQuery object from API response"""
        from_user = User.from_dict(data.get('from')) if data.get('from') else None
        
        return cls(
            id=data.get('id'),
            from_user=from_user,
            query=data.get('query'),
            offset=data.get('offset'),
            chat_type=data.get('chat_type'),
            location=data.get('location')
        )

@dataclass
class InlineQueryResult:
    """Base class for inline query results"""
    type: str
    id: str

@dataclass
class InputTextMessageContent:
    """Represents the content of a text message to be sent as the result of an inline query"""
    message_text: str
    parse_mode: Optional[str] = None
    disable_web_page_preview: Optional[bool] = None

@dataclass
class InlineQueryResultArticle(InlineQueryResult):
    """Represents a link to an article or web page"""
    title: str
    input_message_content: InputTextMessageContent
    reply_markup: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    hide_url: Optional[bool] = None
    description: Optional[str] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None
    
    def __init__(self, id: str, title: str, input_message_content: InputTextMessageContent, **kwargs):
        super().__init__(type='article', id=id)
        self.title = title
        self.input_message_content = input_message_content
        self.reply_markup = kwargs.get('reply_markup')
        self.url = kwargs.get('url')
        self.hide_url = kwargs.get('hide_url')
        self.description = kwargs.get('description')
        self.thumb_url = kwargs.get('thumb_url')
        self.thumb_width = kwargs.get('thumb_width')
        self.thumb_height = kwargs.get('thumb_height')
