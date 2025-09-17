#!/usr/bin/env python3
"""
Test advanced bot functionality
"""
import asyncio
from pytggram import Client, filters, types

bot = Client("TEST_TOKEN")

# Advanced filter examples
@bot.on_message(filters.Command('admin') & filters.Admin)
async def admin_command(client, message):
    """Admin-only command"""
    await message.reply("Admin command executed!")

@bot.on_message(filters.Text(contains=['urgent', 'important']) & ~filters.Private)
async def urgent_message(client, message):
    """Handle urgent messages in groups"""
    await message.reply("⚠️ This seems important!")

@bot.on_message(filters.Regex(r'^hello.*') | filters.Regex(r'^hi.*'))
async def greeting_handler(client, message):
    """Handle greetings with regex"""
    await message.reply("Hello there! 👋")

@bot.on_message((filters.Command('report') | filters.Text(contains='report')) & filters.Group)
async def report_handler(client, message):
    """Handle reports in groups"""
    await message.reply("Report received! 📋")

async def test_advanced_filters():
    """Test advanced filter combinations"""
    print("Testing advanced filters...")
    
    from fixtures.sample_data import SAMPLE_MESSAGE, SAMPLE_PRIVATE_CHAT
    
    # Test private filter
    private_message = type('Message', (), {
        **SAMPLE_MESSAGE,
        "chat": type('Chat', (), SAMPLE_PRIVATE_CHAT)()
    })()
    
    private_filter = filters.Private()
    assert private_filter.check(private_message) == True
    print("✓ Private filter test passed")
    
    # Test group filter
    group_message = type('Message', (), SAMPLE_MESSAGE)()
    group_filter = filters.Group()
    assert group_filter.check(group_message) == True
    print("✓ Group filter test passed")
    
    # Test text filter
    text_message = type('Message', (), {
        **SAMPLE_MESSAGE,
        "text": "This is urgent!"
    })()
    
    text_filter = filters.Text(contains='urgent')
    assert text_filter.check(text_message) == True
    print("✓ Text filter test passed")

if __name__ == "__main__":
    print("Running advanced bot tests...")
    asyncio.run(test_advanced_filters())
    print("All advanced tests passed! ✅")
