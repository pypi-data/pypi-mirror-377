class PyTgGramException(Exception):
    """Base exception for all PyTgGram errors"""
    pass

class APIException(PyTgGramException):
    """Raised when Telegram API returns an error"""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code

class FloodException(PyTgGramException):
    """Raised when flood control is triggered"""
    def __init__(self, message, retry_after):
        super().__init__(message)
        self.retry_after = retry_after

class TimeoutException(PyTgGramException):
    """Raised when a request times out"""
    pass

class InvalidTokenException(PyTgGramException):
    """Raised when the bot token is invalid"""
    pass

class HandlerException(PyTgGramException):
    """Raised when there's an issue with handlers"""
    pass

class DatabaseException(PyTgGramException):
    """Raised when there's a database error"""
    pass

class FilterException(PyTgGramException):
    """Raised when there's a filter error"""
    pass
