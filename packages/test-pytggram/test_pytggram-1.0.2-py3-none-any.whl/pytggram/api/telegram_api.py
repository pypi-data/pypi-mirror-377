"""
Telegram Bot API wrapper utilities
"""
import aiohttp
from typing import Dict, Any, Optional
from ..exceptions import APIException, FloodException

class TelegramAPI:
    """Low-level Telegram API wrapper"""
    
    def __init__(self, token: str, session: aiohttp.ClientSession = None):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.session = session or aiohttp.ClientSession()
    
    async def make_request(self, method: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to Telegram API"""
        url = f"{self.api_url}/{method}"
        
        try:
            async with self.session.post(url, json=data) as response:
                result = await response.json()
                
                if result.get('ok'):
                    return result
                else:
                    error_code = result.get('error_code')
                    description = result.get('description', 'Unknown error')
                    
                    if 'retry after' in description.lower() or error_code == 429:
                        retry_after = int(description.split()[-1]) if 'retry after' in description else 1
                        raise FloodException(f"Flood control: retry after {retry_after} seconds", retry_after)
                    
                    raise APIException(description, error_code)
                    
        except Exception as e:
            raise APIException(f"API request failed: {e}")
    
    async def close(self):
        """Close the session"""
        if not self.session.closed:
            await self.session.close()
