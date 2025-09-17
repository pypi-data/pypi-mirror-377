import re
from typing import Pattern, List, Optional, Callable
from .types import Message, CallbackQuery, InlineQuery, Poll, PollAnswer
from .exceptions import FilterException

class Filter:
    """Base class for all filters"""
    def __call__(self, update) -> bool:
        return self.check(update)
    
    def check(self, update) -> bool:
        raise NotImplementedError("Filter subclasses must implement check() method")
    
    def __and__(self, other):
        return AndFilter(self, other)
    
    def __or__(self, other):
        return OrFilter(self, other)
    
    def __invert__(self):
        return InvertFilter(self)

class AndFilter(Filter):
    """Logical AND filter"""
    def __init__(self, *filters):
        self.filters = filters
    
    def check(self, update) -> bool:
        return all(f.check(update) for f in self.filters)

class OrFilter(Filter):
    """Logical OR filter"""
    def __init__(self, *filters):
        self.filters = filters
    
    def check(self, update) -> bool:
        return any(f.check(update) for f in self.filters)

class InvertFilter(Filter):
    """Logical NOT filter"""
    def __init__(self, filter):
        self.filter = filter
    
    def check(self, update) -> bool:
        return not self.filter.check(update)

class Command(Filter):
    """Filter for command messages"""
    def __init__(self, commands: List[str] = None, prefixes: str = '/', case_sensitive: bool = False):
        self.commands = commands
        self.prefixes = prefixes
        self.case_sensitive = case_sensitive
    
    def check(self, update) -> bool:
        if not isinstance(update, Message) or not update.text:
            return False
        
        text = update.text if self.case_sensitive else update.text.lower()
        
        for prefix in self.prefixes:
            if text.startswith(prefix):
                command = text.split()[0][len(prefix):]
                if not self.case_sensitive:
                    command = command.lower()
                
                if self.commands is None:
                    return True
                
                if command in self.commands:
                    return True
        
        return False

class Text(Filter):
    """Filter for text messages"""
    def __init__(self, text: str = None, contains: str = None, ignore_case: bool = False):
        self.text = text
        self.contains = contains
        self.ignore_case = ignore_case
    
    def check(self, update) -> bool:
        if not isinstance(update, Message) or not update.text:
            return False
        
        text = update.text.lower() if self.ignore_case else update.text
        
        if self.text:
            compare_text = self.text.lower() if self.ignore_case else self.text
            return text == compare_text
        
        if self.contains:
            compare_contains = self.contains.lower() if self.ignore_case else self.contains
            return compare_contains in text
        
        return bool(text)

class Regex(Filter):
    """Filter for messages matching a regex pattern"""
    def __init__(self, pattern: Pattern):
        self.pattern = pattern
    
    def check(self, update) -> bool:
        if not isinstance(update, Message) or not update.text:
            return False
        
        return bool(self.pattern.search(update.text))

class CallbackData(Filter):
    """Filter for callback queries with specific data"""
    def __init__(self, data: str = None, contains: str = None, startswith: str = None, endswith: str = None):
        self.data = data
        self.contains = contains
        self.startswith = startswith
        self.endswith = endswith
    
    def check(self, update) -> bool:
        if not isinstance(update, CallbackQuery) or not update.data:
            return False
        
        if self.data:
            return update.data == self.data
        
        if self.contains:
            return self.contains in update.data
        
        if self.startswith:
            return update.data.startswith(self.startswith)
        
        if self.endswith:
            return update.data.endswith(self.endswith)
        
        return bool(update.data)

class InlinePattern(Filter):
    """Filter for inline queries with specific pattern"""
    def __init__(self, pattern: str = None):
        self.pattern = pattern
    
    def check(self, update) -> bool:
        if not isinstance(update, InlineQuery) or not update.query:
            return False
        
        if self.pattern is None:
            return True
        
        return update.query.startswith(self.pattern)

class State(Filter):
    """Filter for user state"""
    def __init__(self, state: str):
        self.state = state
    
    def check(self, update) -> bool:
        # This requires state management to be implemented
        # For now, it's a placeholder
        return False

class Admin(Filter):
    """Filter for admin users"""
    def check(self, update) -> bool:
        # This requires admin list management
        # For now, it's a placeholder
        return False

class Private(Filter):
    """Filter for private chats"""
    def check(self, update) -> bool:
        if isinstance(update, Message) and update.chat:
            return update.chat.type == 'private'
        return False

class Group(Filter):
    """Filter for group chats"""
    def check(self, update) -> bool:
        if isinstance(update, Message) and update.chat:
            return update.chat.type in ['group', 'supergroup']
        return False

class Channel(Filter):
    """Filter for channel chats"""
    def check(self, update) -> bool:
        if isinstance(update, Message) and update.chat:
            return update.chat.type == 'channel'
        return False
