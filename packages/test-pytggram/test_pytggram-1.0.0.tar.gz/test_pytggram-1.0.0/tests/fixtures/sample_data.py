"""
Sample data for tests
"""

# Sample user data
SAMPLE_USER = {
    "id": 123456789,
    "is_bot": False,
    "first_name": "Hasnain",
    "last_name": "Khan",
    "username": "hasnainkk",
    "language_code": "en"
}

# Sample chat data
SAMPLE_CHAT = {
    "id": -100123456789,
    "type": "supergroup",
    "title": "Test Group",
    "username": "testgroup"
}

# Sample private chat
SAMPLE_PRIVATE_CHAT = {
    "id": 123456789,
    "type": "private",
    "first_name": "Hasnain",
    "last_name": "Khan",
    "username": "hasnainkk"
}

# Sample message data
SAMPLE_MESSAGE = {
    "message_id": 1,
    "from": SAMPLE_USER,
    "chat": SAMPLE_CHAT,
    "date": 1640995200,
    "text": "/start"
}

# Sample callback query
SAMPLE_CALLBACK = {
    "id": "123456789",
    "from": SAMPLE_USER,
    "message": SAMPLE_MESSAGE,
    "chat_instance": "123456789",
    "data": "button_click"
}

# Sample inline query
SAMPLE_INLINE_QUERY = {
    "id": "123456789",
    "from": SAMPLE_USER,
    "query": "search term",
    "offset": "0"
}

# Sample poll
SAMPLE_POLL = {
    "id": "123456789",
    "question": "Test question?",
    "options": [
        {"text": "Option 1", "voter_count": 0},
        {"text": "Option 2", "voter_count": 0}
    ],
    "total_voter_count": 0,
    "is_closed": False,
    "is_anonymous": True,
    "type": "regular",
    "allows_multiple_answers": False
}
