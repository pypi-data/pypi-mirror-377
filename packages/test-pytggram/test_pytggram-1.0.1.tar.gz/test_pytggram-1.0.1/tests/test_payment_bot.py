#!/usr/bin/env python3
"""
Test payment functionality
"""
import asyncio
from pytggram import Client, filters, types

bot = Client("TEST_TOKEN")

@bot.command(['donate'])
async def donate_command(client, message):
    """Donation command"""
    from pytggram.types import LabeledPrice
    
    prices = [LabeledPrice(label="Donation", amount=500)]  # 5.00 USD
    
    await client.send_invoice(
        chat_id=message.chat.id,
        title="Donation",
        description="Support our bot development",
        payload="donation_123",
        provider_token="TEST_PROVIDER_TOKEN",
        currency="USD",
        prices=prices,
        start_parameter="donate"
    )

@bot.on_message(filters.SuccessfulPayment)
async def successful_payment(client, message):
    """Handle successful payment"""
    await message.reply(
        f"Thank you for your donation of {message.successful_payment.total_amount / 100} "
        f"{message.successful_payment.currency}!"
    )

@bot.on_message(filters.PreCheckoutQuery)
async def pre_checkout_handler(client, pre_checkout_query):
    """Handle pre-checkout queries"""
    await client.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

async def test_payment_types():
    """Test payment types"""
    print("Testing payment types...")
    
    from pytggram.types import LabeledPrice, SuccessfulPayment
    
    # Test labeled price
    price = LabeledPrice("Test Item", 1000)  # 10.00 USD
    assert price.label == "Test Item"
    assert price.amount == 1000
    print("✓ Labeled price test passed")
    
    # Test successful payment
    payment = SuccessfulPayment(
        currency="USD",
        total_amount=1000,
        invoice_payload="test_123",
        telegram_payment_charge_id="charge_123",
        provider_payment_charge_id="provider_123"
    )
    
    assert payment.currency == "USD"
    assert payment.total_amount == 1000
    print("✓ Successful payment test passed")

if __name__ == "__main__":
    print("Running payment bot tests...")
    asyncio.run(test_payment_types())
    print("All payment bot tests passed! ✅")
