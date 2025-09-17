#!/usr/bin/env python3
"""
Test error handling
"""
import asyncio
from pytggram import Client, filters, APIException, FloodException

bot = Client("TEST_TOKEN")

@bot.on_message(filters.Command('error'))
async def error_test(client, message):
    """Test error handling"""
    try:
        # Simulate an error
        result = 1 / 0
        await message.reply(f"Result: {result}")
    except ZeroDivisionError as e:
        await message.reply(f"Error: {e}")
    except Exception as e:
        await message.reply(f"Unexpected error: {e}")

@bot.on_message(filters.Command('api_error'))
async def api_error_test(client, message):
    """Test API error handling"""
    try:
        # This would cause an API error with invalid token
        await client.get_me()
    except APIException as e:
        await message.reply(f"API Error: {e} (code: {e.code})")
    except Exception as e:
        await message.reply(f"Unexpected error: {e}")

async def test_exception_handling():
    """Test exception handling"""
    print("Testing exception handling...")
    
    # Test APIException
    try:
        raise APIException("Test API error", 400)
    except APIException as e:
        assert str(e) == "Test API error"
        assert e.code == 400
        print("✓ APIException test passed")
    
    # Test FloodException
    try:
        raise FloodException("Test flood error", 5)
    except FloodException as e:
        assert str(e) == "Test flood error"
        assert e.retry_after == 5
        print("✓ FloodException test passed")
    
    # Test error handling in bot
    from fixtures.sample_data import SAMPLE_MESSAGE
    
    class MockClient:
        async def get_me(self):
            raise APIException("Test error", 500)
    
    message = type('Message', (), SAMPLE_MESSAGE)()
    message.reply = lambda text: print(f"Error handling reply: {text}")
    
    await api_error_test(MockClient(), message)
    print("✓ Bot error handling test passed")

if __name__ == "__main__":
    print("Running error handling tests...")
    asyncio.run(test_exception_handling())
    print("All error handling tests passed! ✅")
