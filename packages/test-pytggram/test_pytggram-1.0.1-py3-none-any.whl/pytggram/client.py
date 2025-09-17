import asyncio
import aiohttp
import time
from typing import List, Callable, Optional, Dict, Any
from .exceptions import InvalidTokenException, APIException, FloodException
from .utils import setup_logger
from .handlers import MessageHandler, CallbackHandler, InlineHandler, PollHandler
from .storage import MemoryStorage
from .dispatcher import Dispatcher
from .router import Router

class Client:
    """Advanced client for interacting with the Telegram Bot API with flood control"""
    
    def __init__(self, token: str, session: aiohttp.ClientSession = None, 
                 max_retries: int = 3, request_timeout: int = 30,
                 flood_sleep_threshold: int = 10):
        if not token or ':' not in token:
            raise InvalidTokenException("Invalid bot token provided")
        
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.session = session or aiohttp.ClientSession()
        self.logger = setup_logger('pytggram')
        self.storage = MemoryStorage()
        
        self.dispatcher = Dispatcher()
        self.router = Router()
        self.running = False
        self.last_update_id = 0
        
        # Flood control settings
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        self.flood_sleep_threshold = flood_sleep_threshold
        self.last_request_time = 0
        
        # Auto-register built-in handlers
        self._register_builtin_handlers()
    
    def _register_builtin_handlers(self):
        """Register built-in handlers for convenience"""
        self.dispatcher.add_handler(MessageHandler(self._handle_message))
        self.dispatcher.add_handler(CallbackHandler(self._handle_callback))
        self.dispatcher.add_handler(InlineHandler(self._handle_inline))
        self.dispatcher.add_handler(PollHandler(self._handle_poll))
    
    async def _handle_message(self, client, message):
        """Default message handler that routes to decorated handlers"""
        await self.router.route_message(message)
    
    async def _handle_callback(self, client, callback_query):
        """Default callback handler that routes to decorated handlers"""
        await self.router.route_callback(callback_query)
    
    async def _handle_inline(self, client, inline_query):
        """Default inline handler that routes to decorated handlers"""
        await self.router.route_inline(inline_query)
    
    async def _handle_poll(self, client, poll):
        """Default poll handler that routes to decorated handlers"""
        await self.router.route_poll(poll)
    
    def on_message(self, filters=None, group: int = 0):
        """Decorator to register a message handler"""
        def decorator(func):
            handler = MessageHandler(func, filters, group)
            self.dispatcher.add_handler(handler)
            return func
        return decorator
    
    def on_callback(self, filters=None, group: int = 0):
        """Decorator to register a callback handler"""
        def decorator(func):
            handler = CallbackHandler(func, filters, group)
            self.dispatcher.add_handler(handler)
            return func
        return decorator
    
    def on_inline(self, filters=None, group: int = 0):
        """Decorator to register an inline handler"""
        def decorator(func):
            handler = InlineHandler(func, filters, group)
            self.dispatcher.add_handler(handler)
            return func
        return decorator
    
    def on_poll(self, filters=None, group: int = 0):
        """Decorator to register a poll handler"""
        def decorator(func):
            handler = PollHandler(func, filters, group)
            self.dispatcher.add_handler(handler)
            return func
        return decorator
    
    def command(self, commands, prefixes='/', case_sensitive=False, group: int = 0):
        """Decorator to register a command handler"""
        from .filters import Command
        return self.on_message(Command(commands, prefixes, case_sensitive), group)
    
    def inline_handler(self, pattern=None, group: int = 0):
        """Decorator to register an inline query handler"""
        from .filters import InlinePattern
        return self.on_inline(InlinePattern(pattern), group)
    
    async def _make_request(self, method: str, data: Dict[str, Any] = None, 
                          retry_count: int = 0) -> Dict[str, Any]:
        """Make a request to Telegram API with flood control and retry logic"""
        url = f"{self.api_url}/{method}"
        
        # Add delay between requests to avoid flood
        current_time = time.time()
        if current_time - self.last_request_time < 0.1:  # 100ms between requests
            await asyncio.sleep(0.1)
        self.last_request_time = time.time()
        
        try:
            async with self.session.post(url, json=data, timeout=self.request_timeout) as response:
                result = await response.json()
                
                if result.get('ok'):
                    return result
                else:
                    error_code = result.get('error_code')
                    description = result.get('description', 'Unknown error')
                    
                    # Handle flood control
                    if 'retry after' in description.lower() or error_code == 429:
                        retry_after = int(description.split()[-1]) if 'retry after' in description else 1
                        raise FloodException(f"Flood control: retry after {retry_after} seconds", retry_after)
                    
                    raise APIException(description, error_code)
                    
        except asyncio.TimeoutError:
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self._make_request(method, data, retry_count + 1)
            raise APIException("Request timeout after multiple retries")
    
    async def get_updates(self, timeout: int = 30, allowed_updates: List[str] = None):
        """Get updates from Telegram with flood control"""
        params = {
            'timeout': timeout,
            'offset': self.last_update_id + 1
        }
        
        if allowed_updates:
            params['allowed_updates'] = allowed_updates
        
        try:
            result = await self._make_request('getUpdates', params)
            return result.get('result', [])
        except FloodException as e:
            self.logger.warning(f"Flood control active, sleeping for {e.retry_after} seconds")
            await asyncio.sleep(e.retry_after)
            return []
    
    async def process_updates(self, updates):
        """Process incoming updates"""
        for update in updates:
            self.last_update_id = max(self.last_update_id, update.get('update_id', 0))
            await self.dispatcher.process_update(self, update)
    
    async def start(self, poll_interval: float = 0.1, allowed_updates: List[str] = None):
        """Start the bot with enhanced polling"""
        self.running = True
        
        # Test the token
        bot_info = await self.get_me()
        self.logger.info(f"Bot started as @{bot_info.username} (ID: {bot_info.id})")
        
        # Main loop with error handling
        while self.running:
            try:
                updates = await self.get_updates(allowed_updates=allowed_updates)
                if updates:
                    await self.process_updates(updates)
                
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def stop(self):
        """Stop the bot gracefully"""
        self.running = False
        if not self.session.closed:
            await self.session.close()
    
    def run(self, poll_interval: float = 0.1, allowed_updates: List[str] = None):
        """Run the bot until stopped with better error handling"""
        loop = asyncio.get_event_loop()
        
        try:
            self.logger.info("Starting bot...")
            loop.run_until_complete(self.start(poll_interval, allowed_updates))
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Bot crashed: {e}")
        finally:
            loop.run_until_complete(self.stop())
    
    # Make all API methods available directly on client
    async def get_me(self):
        from .methods import get_me
        return await get_me(self)
    
    async def send_message(self, chat_id, text, **kwargs):
        from .methods import send_message
        return await send_message(self, chat_id, text, **kwargs)
    
    async def send_photo(self, chat_id, photo, **kwargs):
        from .methods import send_photo
        return await send_photo(self, chat_id, photo, **kwargs)
    
    async def send_document(self, chat_id, document, **kwargs):
        from .methods import send_document
        return await send_document(self, chat_id, document, **kwargs)
    
    async def answer_callback_query(self, callback_query_id, **kwargs):
        from .methods import answer_callback_query
        return await answer_callback_query(self, callback_query_id, **kwargs)
    
    async def answer_inline_query(self, inline_query_id, results, **kwargs):
        from .methods import answer_inline_query
        return await answer_inline_query(self, inline_query_id, results, **kwargs)
