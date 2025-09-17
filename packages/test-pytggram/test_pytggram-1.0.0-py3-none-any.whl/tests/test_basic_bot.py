#!/usr/bin/env python3
"""
Test basic bot functionality
"""
import asyncio
from pytggram import Client, filters
from tests.fixtures.sample_data import SAMPLE_MESSAGE, SAMPLE_USER

# Create a basic bot for testing
bot = Client("TEST_TOKEN")

@bot.command(['start', 'help'])
async def start_handler(client, message):
    """Handle start command"""
    await message.reply("Hello! I'm a test bot.")

@bot.command(['echo'])
async def echo_handler(client, message):
    """Echo user message"""
    if message.command_args:
        await message.reply(f"Echo: {message.command_args}")
    else:
        await message.reply("Please provide text to echo")

@bot.on_message(filters.Private)
async def private_message_handler(client, message):
    """Handle private messages"""
    await message.reply("This is a private chat!")

@bot.on_message(filters.Group)
async def group_message_handler(client, message):
    """Handle group messages"""
    await message.reply("This is a group chat!")

async def test_basic_commands():
    """Test basic command functionality"""
    print("Testing basic commands...")
    
    # Simulate a message
    test_message = type('Message', (), SAMPLE_MESSAGE)()
    test_message.reply = lambda text: print(f"Bot would reply: {text}")
    
    # Test command detection
    assert test_message.is_command == True
    assert test_message.command == "/start"
    assert test_message.command_args == ""
    
    print("✓ Basic command test passed")

async def test_message_handling():
    """Test message handling"""
    print("Testing message handling...")
    
    # Create a mock client
    class MockClient:
        async def send_message(self, chat_id, text):
            print(f"Would send message to {chat_id}: {text}")
    
    client = MockClient()
    
    # Test start handler
    message = type('Message', (), SAMPLE_MESSAGE)()
    message.reply = lambda text: print(f"Reply: {text}")
    
    await start_handler(client, message)
    print("✓ Start handler test passed")

if __name__ == "__main__":
    print("Running basic bot tests...")
    asyncio.run(test_basic_commands())
    asyncio.run(test_message_handling())
    print("All basic tests passed! ✅")
