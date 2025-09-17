import redis
from typing import Any, Optional

class RedisStorage:
    """Redis-based storage for bot data"""
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
    
    def get(self, key, default=None):
        value = self.redis.get(key)
        return value if value is not None else default
    
    def set(self, key, value, ex=None):
        self.redis.set(key, value, ex=ex)
    
    def delete(self, key):
        self.redis.delete(key)
    
    def clear(self):
        self.redis.flushdb()
    
    def keys(self, pattern='*'):
        return self.redis.keys(pattern)
