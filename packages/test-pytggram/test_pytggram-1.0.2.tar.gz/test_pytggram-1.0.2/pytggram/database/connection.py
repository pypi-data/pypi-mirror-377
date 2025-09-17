import motor.motor_asyncio
from typing import Optional
from ..utils import setup_logger

class MongoDBConnection:
    """MongoDB connection manager"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, connection_string: str = None, db_name: str = "pytggram"):
        if not hasattr(self, 'initialized'):
            self.logger = setup_logger('pytggram.mongodb')
            self.connection_string = connection_string or "mongodb://localhost:27017"
            self.db_name = db_name
            self.initialized = True
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                self.connection_string,
                maxPoolSize=100,
                minPoolSize=10,
                retryWrites=True,
                w="majority"
            )
            
            # Test connection
            await self._client.admin.command('ping')
            self._db = self._client[self.db_name]
            
            self.logger.info(f"Connected to MongoDB: {self.connection_string}")
            self.logger.info(f"Database: {self.db_name}")
            
            # Create indexes
            await self._create_indexes()
            
            return True
        except Exception as e:
            self.logger.error(f"MongoDB connection failed: {e}")
            return False
    
    async def _create_indexes(self):
        """Create necessary indexes"""
        # Users collection indexes
        await self._db.users.create_index("user_id", unique=True)
        await self._db.users.create_index("username")
        
        # Chats collection indexes
        await self._db.chats.create_index("chat_id", unique=True)
        await self._db.chats.create_index("type")
        
        # Messages collection indexes
        await self._db.messages.create_index("message_id")
        await self._db.messages.create_index("chat_id")
        await self._db.messages.create_index([("chat_id", 1), ("message_id", 1)], unique=True)
        await self._db.messages.create_index("date", expireAfterSeconds=60*60*24*30)  # 30 days TTL
        
        # User data collection indexes
        await self._db.user_data.create_index([("user_id", 1), ("key", 1)], unique=True)
        
        # Chat data collection indexes
        await self._db.chat_data.create_index([("chat_id", 1), ("key", 1)], unique=True)
        
        self.logger.info("MongoDB indexes created successfully")
    
    def get_database(self):
        """Get database instance"""
        return self._db
    
    async def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self.logger.info("MongoDB connection closed")
    
    async def is_connected(self):
        """Check if connected to MongoDB"""
        try:
            await self._client.admin.command('ping')
            return True
        except:
            return False
