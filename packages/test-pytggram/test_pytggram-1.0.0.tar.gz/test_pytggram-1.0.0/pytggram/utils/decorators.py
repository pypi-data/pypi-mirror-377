from functools import wraps
from typing import Callable

def handler(filters=None):
    """Decorator to register a message handler"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(client, update):
            return func(client, update)
        wrapper._handler = True
        wrapper._filters = filters
        return wrapper
    return decorator

def command(commands, prefixes='/', case_sensitive=False):
    """Decorator to register a command handler"""
    from ..filters import Command
    return handler(Command(commands, prefixes, case_sensitive))
