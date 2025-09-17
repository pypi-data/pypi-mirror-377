#!/usr/bin/env python3
"""
Test handler system
"""
import asyncio
from pytggram.handlers import MessageHandler, CallbackHandler, InlineHandler, PollHandler
from pytggram.filters import Command, CallbackData
from tests.fixtures.sample_data import SAMPLE_MESSAGE, SAMPLE_CALLBACK, SAMPLE_INLINE_QUERY, SAMPLE_POLL

async def test_message_handler():
    """Test message handler"""
    print("Testing message handler...")
    
    async def mock_callback(client, message):
        print(f"Handler called with: {message.text}")
    
    # Create handler with filter
    handler = MessageHandler(mock_callback, Command('start'))
    
    # Test message matching filter
    message = type('Message', (), SAMPLE_MESSAGE)()
    assert handler.check(message) == True
    print("✓ Message handler filter test passed")
    
    # Test handler execution
    class MockClient:
        pass
    
    await handler.handle(MockClient(), {"message": SAMPLE_MESSAGE})
    print("✓ Message handler execution test passed")

async def test_callback_handler():
    """Test callback handler"""
    print("Testing callback handler...")
    
    async def mock_callback(client, callback):
        print(f"Callback handler called with: {callback.data}")
    
    # Create handler with filter
    handler = CallbackHandler(mock_callback, CallbackData('button_click'))
    
    # Test callback matching filter
    callback = type('CallbackQuery', (), SAMPLE_CALLBACK)()
    assert handler.check(callback) == True
    print("✓ Callback handler filter test passed")
    
    # Test handler execution
    class MockClient:
        pass
    
    await handler.handle(MockClient(), {"callback_query": SAMPLE_CALLBACK})
    print("✓ Callback handler execution test passed")

async def test_inline_handler():
    """Test inline handler"""
    print("Testing inline handler...")
    
    async def mock_callback(client, inline_query):
        print(f"Inline handler called with: {inline_query.query}")
    
    # Create handler
    handler = InlineHandler(mock_callback)
    
    # Test handler execution
    class MockClient:
        pass
    
    await handler.handle(MockClient(), {"inline_query": SAMPLE_INLINE_QUERY})
    print("✓ Inline handler execution test passed")

async def test_poll_handler():
    """Test poll handler"""
    print("Testing poll handler...")
    
    async def mock_callback(client, poll):
        print(f"Poll handler called with: {poll.question}")
    
    # Create handler
    handler = PollHandler(mock_callback)
    
    # Test handler execution
    class MockClient:
        pass
    
    await handler.handle(MockClient(), {"poll": SAMPLE_POLL})
    print("✓ Poll handler execution test passed")

if __name__ == "__main__":
    print("Running handler tests...")
    asyncio.run(test_message_handler())
    asyncio.run(test_callback_handler())
    asyncio.run(test_inline_handler())
    asyncio.run(test_poll_handler())
    print("All handler tests passed! ✅")
