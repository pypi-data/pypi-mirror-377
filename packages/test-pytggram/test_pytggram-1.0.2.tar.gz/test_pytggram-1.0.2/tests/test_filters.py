#!/usr/bin/env python3
"""
Test filter system
"""
import re
from pytggram.filters import Command, Text, Regex, Private, Group, CallbackData, InlinePattern
from tests.fixtures.sample_data import SAMPLE_MESSAGE, SAMPLE_CALLBACK, SAMPLE_INLINE_QUERY

def test_command_filter():
    """Test command filter"""
    print("Testing command filter...")
    
    # Create test message
    message = type('Message', (), SAMPLE_MESSAGE)()
    
    # Test command filter
    filter = Command(['start', 'help'])
    assert filter.check(message) == True
    print("✓ Command filter test passed")
    
    # Test with different command
    other_message = type('Message', (), {
        **SAMPLE_MESSAGE,
        "text": "/unknown"
    })()
    assert filter.check(other_message) == False
    print("✓ Command filter negative test passed")

def test_text_filter():
    """Test text filter"""
    print("Testing text filter...")
    
    # Test contains filter
    message = type('Message', (), {
        **SAMPLE_MESSAGE,
        "text": "Hello world"
    })()
    
    filter = Text(contains='world')
    assert filter.check(message) == True
    print("✓ Text contains filter test passed")
    
    # Test startswith filter
    filter = Text(startswith='Hello')
    assert filter.check(message) == True
    print("✓ Text startswith filter test passed")
    
    # Test endswith filter
    filter = Text(endswith='world')
    assert filter.check(message) == True
    print("✓ Text endswith filter test passed")

def test_regex_filter():
    """Test regex filter"""
    print("Testing regex filter...")
    
    message = type('Message', (), {
        **SAMPLE_MESSAGE,
        "text": "Hello 123 world"
    })()
    
    # Test regex filter
    filter = Regex(re.compile(r'\d+'))
    assert filter.check(message) == True
    print("✓ Regex filter test passed")

def test_chat_type_filters():
    """Test chat type filters"""
    print("Testing chat type filters...")
    
    from fixtures.sample_data import SAMPLE_PRIVATE_CHAT
    
    # Test private filter
    private_message = type('Message', (), {
        **SAMPLE_MESSAGE,
        "chat": type('Chat', (), SAMPLE_PRIVATE_CHAT)()
    })()
    
    filter = Private()
    assert filter.check(private_message) == True
    print("✓ Private filter test passed")
    
    # Test group filter
    group_message = type('Message', (), SAMPLE_MESSAGE)()
    filter = Group()
    assert filter.check(group_message) == True
    print("✓ Group filter test passed")

def test_callback_filter():
    """Test callback filter"""
    print("Testing callback filter...")
    
    callback = type('CallbackQuery', (), SAMPLE_CALLBACK)()
    
    # Test callback data filter
    filter = CallbackData('button_click')
    assert filter.check(callback) == True
    print("✓ Callback filter test passed")
    
    # Test callback contains filter
    filter = CallbackData(contains='button')
    assert filter.check(callback) == True
    print("✓ Callback contains filter test passed")

def test_inline_filter():
    """Test inline filter"""
    print("Testing inline filter...")
    
    inline_query = type('InlineQuery', (), SAMPLE_INLINE_QUERY)()
    
    # Test inline pattern filter
    filter = InlinePattern('search')
    assert filter.check(inline_query) == True
    print("✓ Inline filter test passed")

def test_filter_combinations():
    """Test filter combinations"""
    print("Testing filter combinations...")
    
    message = type('Message', (), {
        **SAMPLE_MESSAGE,
        "text": "Hello world"
    })()
    
    # Test AND combination
    combined_filter = Text(contains='Hello') & Text(contains='world')
    assert combined_filter.check(message) == True
    print("✓ AND filter combination test passed")
    
    # Test OR combination
    combined_filter = Text(contains='Hello') | Text(contains='goodbye')
    assert combined_filter.check(message) == True
    print("✓ OR filter combination test passed")
    
    # Test NOT combination
    combined_filter = Text(contains='Hello') & ~Text(contains='goodbye')
    assert combined_filter.check(message) == True
    print("✓ NOT filter combination test passed")

if __name__ == "__main__":
    print("Running filter tests...")
    test_command_filter()
    test_text_filter()
    test_regex_filter()
    test_chat_type_filters()
    test_callback_filter()
    test_inline_filter()
    test_filter_combinations()
    print("All filter tests passed! ✅")
