import asyncio
import time
from functools import wraps
from ..exceptions import FloodException

def flood_control(func):
    """Decorator for flood control on API methods"""
    last_call_time = 0
    flood_wait = 0
    
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        nonlocal last_call_time, flood_wait
        
        current_time = time.time()
        
        # Check if we're in flood wait period
        if flood_wait > 0:
            time_since_last_call = current_time - last_call_time
            if time_since_last_call < flood_wait:
                await asyncio.sleep(flood_wait - time_since_last_call)
        
        try:
            result = await func(self, *args, **kwargs)
            last_call_time = time.time()
            flood_wait = 0  # Reset flood wait on success
            return result
        except FloodException as e:
            flood_wait = e.retry_after
            last_call_time = time.time()
            raise e
    
    return wrapper
