import asyncio
import threading
from typing import List, Optional
from .client import Client
from .exceptions import PyTgGramException

class SyncClient:
    """Synchronous client for those who prefer sync programming"""
    
    def __init__(self, token: str, **kwargs):
        self._async_client = Client(token, **kwargs)
        self._loop = asyncio.new_event_loop()
        self._thread = None
    
    def __getattr__(self, name):
        """Delegate method calls to async client"""
        attr = getattr(self._async_client, name)
        
        if callable(attr):
            def sync_wrapper(*args, **kwargs):
                if self._loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(attr(*args, **kwargs), self._loop)
                    return future.result()
                else:
                    return self._loop.run_until_complete(attr(*args, **kwargs))
            return sync_wrapper
        return attr
    
    def run(self, poll_interval: float = 0.1, allowed_updates: List[str] = None):
        """Run the bot in a separate thread"""
        def run_loop():
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(
                self._async_client.start(poll_interval, allowed_updates)
            )
        
        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        
        try:
            self._thread.join()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        self._loop.call_soon_threadsafe(
            lambda: asyncio.create_task(self._async_client.stop())
        )
        if self._thread:
            self._thread.join(timeout=5)
