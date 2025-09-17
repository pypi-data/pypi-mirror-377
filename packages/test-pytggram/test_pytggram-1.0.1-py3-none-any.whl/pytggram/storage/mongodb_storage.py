from typing import Any, Optional, Dict
from ..database.connection import MongoDBConnection
from ..database.crud import MongoDBCRUD
from ..utils import setup_logger

class MongoDBStorage:
    """MongoDB-based storage for bot data"""
    
    def __init__(self, connection_string: str = None, db_name: str = "pytggram"):
        self.logger = setup_logger('pytggram.storage.mongodb')
        self.connection = MongoDBConnection(connection_string, db_name)
        self.crud = None
    
    async def connect(self):
        """Connect to MongoDB"""
        if await self.connection.connect():
            self.crud = MongoDBCRUD(self.connection)
            return True
        return False
    
    async def close(self):
        """Close MongoDB connection"""
        await self.connection.close()
    
    async def is_connected(self):
        """Check if connected to MongoDB"""
        return await self.connection.is_connected()
    
    async def get(self, user_id: int, key: str, default: Any = None) -> Any:
        """Get user data"""
        if not self.crud:
            return default
        
        return await self.crud.get_user_data(user_id, key, default)
    
    async def set(self, user_id: int, key: str, value: Any) -> bool:
        """Set user data"""
        if not self.crud:
            return False
        
        return await self.crud.set_user_data(user_id, key, value)
    
    async def delete(self, user_id: int, key: str) -> bool:
        """Delete user data"""
        if not self.crud:
            return False
        
        return await self.crud.delete_user_data(user_id, key)
    
    async def clear_user_data(self, user_id: int) -> bool:
        """Clear all data for a user"""
        if not self.crud:
            return False
        
        # This would need to be implemented in CRUD
        return False
    
    async def get_chat_data(self, chat_id: int, key: str, default: Any = None) -> Any:
        """Get chat data"""
        if not self.crud:
            return default
        
        return await self.crud.get_chat_data(chat_id, key, default)
    
    async def set_chat_data(self, chat_id: int, key: str, value: Any) -> bool:
        """Set chat data"""
        if not self.crud:
            return False
        
        return await self.crud.set_chat_data(chat_id, key, value)
    
    async def delete_chat_data(self, chat_id: int, key: str) -> bool:
        """Delete chat data"""
        if not self.crud:
            return False
        
        return await self.crud.delete_chat_data(chat_id, key)
