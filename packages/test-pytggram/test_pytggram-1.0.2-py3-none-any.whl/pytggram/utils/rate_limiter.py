import asyncio
import time
from collections import deque

class RateLimiter:
    """Rate limiter for controlling API requests"""
    
    def __init__(self, max_requests: int = 30, period: float = 1.0):
        self.max_requests = max_requests
        self.period = period
        self.requests = deque()
    
    async def acquire(self):
        """Acquire a slot for making a request"""
        now = time.time()
        
        # Remove old requests
        while self.requests and self.requests[0] <= now - self.period:
            self.requests.popleft()
        
        # Check if we've exceeded the rate limit
        if len(self.requests) >= self.max_requests:
            # Wait until the oldest request is old enough
            sleep_time = self.requests[0] + self.period - now
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                # After sleeping, remove old requests again
                while self.requests and self.requests[0] <= now + sleep_time - self.period:
                    self.requests.popleft()
        
        # Add the current request
        self.requests.append(time.time())
