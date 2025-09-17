#!/usr/bin/env python3
"""
Test inline bot functionality
"""
import asyncio
from datetime import datetime
from pytggram import Client, filters, types

bot = Client("TEST_TOKEN")

@bot.inline_handler()
async def inline_query_handler(client, inline_query):
    """Handle inline queries"""
    from pytggram.types import InlineQueryResultArticle, InputTextMessageContent
    
    results = [
        InlineQueryResultArticle(
            id="1",
            title="Hello World",
            input_message_content=InputTextMessageContent("Hello from PyTgGram! 🚀")
        ),
        InlineQueryResultArticle(
            id="2",
            title="Current Time",
            input_message_content=InputTextMessageContent(f"Current time: {datetime.now()}")
        ),
        InlineQueryResultArticle(
            id="3",
            title="User Info",
            input_message_content=InputTextMessageContent(
                f"User: {inline_query.from_user.full_name}\n"
                f"Query: {inline_query.query}"
            )
        )
    ]
    
    await client.answer_inline_query(inline_query.id, results, cache_time=300)

@bot.inline_handler('search')
async def search_inline_handler(client, inline_query):
    """Handle search inline queries"""
    from pytggram.types import InlineQueryResultArticle, InputTextMessageContent
    
    query = inline_query.query.replace('search ', '').strip()
    
    results = [
        InlineQueryResultArticle(
            id="1",
            title=f"Search: {query}",
            input_message_content=InputTextMessageContent(f"Search results for: {query}"),
            description=f"Search for '{query}' in our database"
        )
    ]
    
    await client.answer_inline_query(inline_query.id, results, cache_time=300)

async def test_inline_handling():
    """Test inline query handling"""
    print("Testing inline query handling...")
    
    from fixtures.sample_data import SAMPLE_INLINE_QUERY
    
    # Create mock inline query
    inline_query = type('InlineQuery', (), SAMPLE_INLINE_QUERY)()
    
    # Test inline query properties
    assert inline_query.id == "123456789"
    assert inline_query.query == "search term"
    print("✓ Inline query properties test passed")
    
    # Test inline result creation
    from pytggram.types import InlineQueryResultArticle, InputTextMessageContent
    
    result = InlineQueryResultArticle(
        id="test",
        title="Test Result",
        input_message_content=InputTextMessageContent("Test content")
    )
    
    assert result.type == "article"
    assert result.id == "test"
    assert result.title == "Test Result"
    print("✓ Inline result creation test passed")

if __name__ == "__main__":
    print("Running inline bot tests...")
    asyncio.run(test_inline_handling())
    print("All inline bot tests passed! ✅")
