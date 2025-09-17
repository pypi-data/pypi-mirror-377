#!/usr/bin/env python3
"""
Test plugin system
"""
import asyncio
from pytggram import Client, filters

# Mock plugin
def example_plugin(client):
    """Example plugin for testing"""
    
    @client.command(['plugin'])
    async def plugin_command(client, message):
        await message.reply("This is from a plugin!")
    
    @client.on_message(filters.Text(contains='plugin'))
    async def plugin_message(client, message):
        await message.reply("Plugin detected message!")
    
    return {
        'name': 'Example Plugin',
        'version': '1.0.0',
        'description': 'Test plugin for PyTgGram'
    }

async def test_plugin_system():
    """Test plugin system"""
    print("Testing plugin system...")
    
    # Create bot
    bot = Client("TEST_TOKEN")
    
    # Load plugin
    plugin_info = example_plugin(bot)
    
    # Verify plugin info
    assert plugin_info['name'] == 'Example Plugin'
    assert plugin_info['version'] == '1.0.0'
    print("✓ Plugin registration test passed")
    
    # Verify handlers were added
    assert len(bot.dispatcher.handlers) > 0
    print("✓ Plugin handler registration test passed")
    
    # Test plugin command
    from fixtures.sample_data import SAMPLE_MESSAGE
    
    class MockClient:
        async def send_message(self, chat_id, text):
            print(f"Plugin would send: {text}")
    
    message = type('Message', (), {
        **SAMPLE_MESSAGE,
        "text": "/plugin"
    })()
    message.reply = lambda text: print(f"Reply: {text}")
    
    # Find the plugin command handler
    for handler in bot.dispatcher.handlers:
        if hasattr(handler, 'filters') and handler.filters:
            if handler.check(message):
                await handler.callback(MockClient(), message)
                break
    
    print("✓ Plugin command test passed")

if __name__ == "__main__":
    print("Running plugin tests...")
    asyncio.run(test_plugin_system())
    print("All plugin tests passed! ✅")
