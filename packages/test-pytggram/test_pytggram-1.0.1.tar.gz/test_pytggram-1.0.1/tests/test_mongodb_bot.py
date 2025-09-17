#!/usr/bin/env python3
"""
Test MongoDB integration
"""
import asyncio
from pytggram import Client, MongoDBStorage
from pytggram.database import MongoDBConnection, MongoDBCRUD, User, Chat, Message

async def test_mongodb_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB connection...")
    
    # Create connection
    connection = MongoDBConnection("mongodb://localhost:27017", "test_bot")
    
    # Test connection
    connected = await connection.connect()
    assert connected == True
    print("✓ MongoDB connection test passed")
    
    # Test database access
    db = connection.get_database()
    assert db is not None
    print("✓ Database access test passed")
    
    await connection.close()
    print("✓ Connection close test passed")

async def test_crud_operations():
    """Test CRUD operations"""
    print("Testing CRUD operations...")
    
    connection = MongoDBConnection("mongodb://localhost:27017", "test_bot")
    await connection.connect()
    crud = MongoDBCRUD(connection)
    
    # Test user operations
    user_data = {
        "id": 999888777,
        "is_bot": False,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser"
    }
    
    user = await crud.get_or_create_user(user_data)
    assert user is not None
    assert user.user_id == 999888777
    print("✓ User creation test passed")
    
    # Test user data operations
    await crud.set_user_data(user.user_id, "test_key", "test_value")
    value = await crud.get_user_data(user.user_id, "test_key")
    assert value == "test_value"
    print("✓ User data test passed")
    
    await connection.close()

async def test_storage_integration():
    """Test storage integration"""
    print("Testing storage integration...")
    
    storage = MongoDBStorage("mongodb://localhost:27017", "test_bot")
    connected = await storage.connect()
    assert connected == True
    print("✓ Storage connection test passed")
    
    # Test storage operations
    await storage.set(123456, "test_key", "test_value")
    value = await storage.get(123456, "test_key")
    assert value == "test_value"
    print("✓ Storage operations test passed")
    
    await storage.close()

if __name__ == "__main__":
    print("Running MongoDB tests...")
    asyncio.run(test_mongodb_connection())
    asyncio.run(test_crud_operations())
    asyncio.run(test_storage_integration())
    print("All MongoDB tests passed! ✅")
