from typing import Dict, Any, List, Optional, Union
from bson import ObjectId
from datetime import datetime
from .models import User, Chat, Message, UserData, ChatData
from .connection import MongoDBConnection

class MongoDBCRUD:
    """CRUD operations for MongoDB"""
    
    def __init__(self, db_connection: MongoDBConnection):
        self.db = db_connection.get_database()
        self.logger = db_connection.logger
    
    # User operations
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by user_id"""
        try:
            user_data = await self.db.users.find_one({"user_id": user_id})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            user.updated_at = datetime.utcnow()
            result = await self.db.users.insert_one(user.to_dict())
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"Error creating user {user.user_id}: {e}")
            return False
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    async def get_or_create_user(self, user_data: Dict[str, Any]) -> User:
        """Get user or create if not exists"""
        user = await self.get_user(user_data['id'])
        if not user:
            user = User(
                user_id=user_data['id'],
                is_bot=user_data.get('is_bot', False),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                username=user_data.get('username'),
                language_code=user_data.get('language_code')
            )
            await self.create_user(user)
        return user
    
    # Chat operations
    async def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get chat by chat_id"""
        try:
            chat_data = await self.db.chats.find_one({"chat_id": chat_id})
            if chat_data:
                return Chat.from_dict(chat_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting chat {chat_id}: {e}")
            return None
    
    async def create_chat(self, chat: Chat) -> bool:
        """Create a new chat"""
        try:
            chat.updated_at = datetime.utcnow()
            result = await self.db.chats.insert_one(chat.to_dict())
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"Error creating chat {chat.chat_id}: {e}")
            return False
    
    async def update_chat(self, chat_id: int, update_data: Dict[str, Any]) -> bool:
        """Update chat data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = await self.db.chats.update_one(
                {"chat_id": chat_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error updating chat {chat_id}: {e}")
            return False
    
    async def get_or_create_chat(self, chat_data: Dict[str, Any]) -> Chat:
        """Get chat or create if not exists"""
        chat = await self.get_chat(chat_data['id'])
        if not chat:
            chat = Chat(
                chat_id=chat_data['id'],
                type=chat_data.get('type'),
                title=chat_data.get('title'),
                username=chat_data.get('username'),
                first_name=chat_data.get('first_name'),
                last_name=chat_data.get('last_name')
            )
            await self.create_chat(chat)
        return chat
    
    # Message operations
    async def save_message(self, message: Message) -> bool:
        """Save a message to database"""
        try:
            result = await self.db.messages.insert_one(message.to_dict())
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"Error saving message {message.message_id}: {e}")
            return False
    
    async def get_message(self, chat_id: int, message_id: int) -> Optional[Message]:
        """Get message by chat_id and message_id"""
        try:
            message_data = await self.db.messages.find_one({
                "chat_id": chat_id,
                "message_id": message_id
            })
            if message_data:
                return Message.from_dict(message_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting message {message_id}: {e}")
            return None
    
    async def get_chat_messages(self, chat_id: int, limit: int = 100, 
                               skip: int = 0) -> List[Message]:
        """Get messages from a chat"""
        try:
            cursor = self.db.messages.find({"chat_id": chat_id}) \
                .sort("date", -1) \
                .skip(skip) \
                .limit(limit)
            
            messages = []
            async for message_data in cursor:
                messages.append(Message.from_dict(message_data))
            
            return messages
        except Exception as e:
            self.logger.error(f"Error getting messages for chat {chat_id}: {e}")
            return []
    
    # User data operations (key-value storage)
    async def set_user_data(self, user_id: int, key: str, value: Any) -> bool:
        """Set user data (key-value pair)"""
        try:
            result = await self.db.user_data.update_one(
                {"user_id": user_id, "key": key},
                {"$set": {"value": value, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"Error setting user data for {user_id}: {e}")
            return False
    
    async def get_user_data(self, user_id: int, key: str, default: Any = None) -> Any:
        """Get user data by key"""
        try:
            data = await self.db.user_data.find_one({"user_id": user_id, "key": key})
            return data['value'] if data else default
        except Exception as e:
            self.logger.error(f"Error getting user data for {user_id}: {e}")
            return default
    
    async def delete_user_data(self, user_id: int, key: str) -> bool:
        """Delete user data by key"""
        try:
            result = await self.db.user_data.delete_one({"user_id": user_id, "key": key})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting user data for {user_id}: {e}")
            return False
    
    # Chat data operations (key-value storage)
    async def set_chat_data(self, chat_id: int, key: str, value: Any) -> bool:
        """Set chat data (key-value pair)"""
        try:
            result = await self.db.chat_data.update_one(
                {"chat_id": chat_id, "key": key},
                {"$set": {"value": value, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"Error setting chat data for {chat_id}: {e}")
            return False
    
    async def get_chat_data(self, chat_id: int, key: str, default: Any = None) -> Any:
        """Get chat data by key"""
        try:
            data = await self.db.chat_data.find_one({"chat_id": chat_id, "key": key})
            return data['value'] if data else default
        except Exception as e:
            self.logger.error(f"Error getting chat data for {chat_id}: {e}")
            return default
    
    async def delete_chat_data(self, chat_id: int, key: str) -> bool:
        """Delete chat data by key"""
        try:
            result = await self.db.chat_data.delete_one({"chat_id": chat_id, "key": key})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting chat data for {chat_id}: {e}")
            return False
    
    # Statistics and analytics
    async def get_user_count(self) -> int:
        """Get total number of users"""
        try:
            return await self.db.users.count_documents({})
        except Exception as e:
            self.logger.error(f"Error getting user count: {e}")
            return 0
    
    async def get_chat_count(self, chat_type: str = None) -> int:
        """Get total number of chats, optionally filtered by type"""
        try:
            query = {"type": chat_type} if chat_type else {}
            return await self.db.chats.count_documents(query)
        except Exception as e:
            self.logger.error(f"Error getting chat count: {e}")
            return 0
    
    async def get_message_count(self, chat_id: int = None) -> int:
        """Get total number of messages, optionally filtered by chat"""
        try:
            query = {"chat_id": chat_id} if chat_id else {}
            return await self.db.messages.count_documents(query)
        except Exception as e:
            self.logger.error(f"Error getting message count: {e}")
            return 0
