#!/usr/bin/env python3
"""
Test rate limiting and flood control
"""
import asyncio
import time
from pytggram.utils import RateLimiter
from pytggram.utils.flood_control import flood_control

async def test_rate_limiter():
    """Test rate limiter"""
    print("Testing rate limiter...")
    
    limiter = RateLimiter(max_requests=5, period=1.0)  # 5 requests per second
    
    # Test acquiring slots
    start_time = time.time()
    for i in range(5):
        await limiter.acquire()
    
    duration = time.time() - start_time
    assert duration < 0.1  # Should be very fast
    print("✓ Rate limiter acquisition test passed")
    
    # Test rate limiting
    start_time = time.time()
    for i in range(6):  # One more than limit
        await limiter.acquire()
    
    duration = time.time() - start_time
    assert duration >= 1.0  # Should have waited
    print("✓ Rate limiter throttling test passed")

async def test_flood_control():
    """Test flood control decorator"""
    print("Testing flood control...")
    
    class TestClient:
        def __init__(self):
            self.call_count = 0
        
        @flood_control
        async def make_request(self):
            self.call_count += 1
            if self.call_count == 1:
                raise FloodException("Test flood", 2)
            return "success"
    
    client = TestClient()
    
    # First call should raise flood exception
    try:
        await client.make_request()
        assert False, "Should have raised FloodException"
    except FloodException:
        print("✓ Flood control exception test passed")
    
    # Second call should succeed after waiting
    result = await client.make_request()
    assert result == "success"
    print("✓ Flood control recovery test passed")

if __name__ == "__main__":
    print("Running rate limiting tests...")
    asyncio.run(test_rate_limiter())
    asyncio.run(test_flood_control())
    print("All rate limiting tests passed! ✅")
