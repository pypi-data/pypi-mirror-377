#!/usr/bin/env python3
"""
Test keyboard and button functionality
"""
import asyncio
from pytggram import Client, filters, types

bot = Client("TEST_TOKEN")

@bot.command(['start'])
async def start_with_keyboard(client, message):
    """Start command with reply keyboard"""
    from pytggram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("Option 1"), KeyboardButton("Option 2")],
        [KeyboardButton("Contact", request_contact=True)],
        [KeyboardButton("Location", request_location=True)]
    ], resize_keyboard=True)
    
    await message.reply("Choose an option:", reply_markup=keyboard)

@bot.command(['inline'])
async def inline_keyboard(client, message):
    """Command with inline keyboard"""
    from pytggram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Button 1", callback_data="btn_1")],
        [InlineKeyboardButton("Button 2", callback_data="btn_2")],
        [InlineKeyboardButton("Website", url="https://example.com")]
    ])
    
    await message.reply("Inline keyboard:", reply_markup=keyboard)

@bot.on_message(filters.Text("Option 1"))
async def option1_handler(client, message):
    await message.reply("You selected Option 1!")

@bot.on_message(filters.Text("Option 2"))
async def option2_handler(client, message):
    await message.reply("You selected Option 2!")

@bot.on_callback(filters.CallbackData(startswith='btn_'))
async def button_handler(client, callback):
    await callback.answer(f"You clicked {callback.data}!")

async def test_keyboard_creation():
    """Test keyboard creation"""
    print("Testing keyboard creation...")
    
    from pytggram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
    
    # Test reply keyboard
    reply_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("Test Button")]
    ])
    
    assert isinstance(reply_keyboard, ReplyKeyboardMarkup)
    print("✓ Reply keyboard creation test passed")
    
    # Test inline keyboard
    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Test", callback_data="test")]
    ])
    
    assert isinstance(inline_keyboard, InlineKeyboardMarkup)
    print("✓ Inline keyboard creation test passed")
    
    # Test button creation
    button = KeyboardButton("Test")
    assert button.text == "Test"
    print("✓ Button creation test passed")
    
    inline_button = InlineKeyboardButton("Test", callback_data="test")
    assert inline_button.text == "Test"
    assert inline_button.callback_data == "test"
    print("✓ Inline button creation test passed")

if __name__ == "__main__":
    print("Running keyboard bot tests...")
    asyncio.run(test_keyboard_creation())
    print("All keyboard bot tests passed! ✅")
