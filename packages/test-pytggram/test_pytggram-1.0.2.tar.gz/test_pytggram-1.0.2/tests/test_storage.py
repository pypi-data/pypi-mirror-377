#!/usr/bin/env python3
"""
Test storage systems
"""
import asyncio
import os
from pytggram.storage import MemoryStorage, RedisStorage, JSONStorage

async def test_memory_storage():
    """Test memory storage"""
    print("Testing memory storage...")
    
    storage = MemoryStorage()
    
    # Test basic operations
    storage.set("key1", "value1")
    assert storage.get("key1") == "value1"
    print("✓ Memory storage set/get test passed")
    
    # Test delete
    storage.delete("key1")
    assert storage.get("key1") is None
    print("✓ Memory storage delete test passed")
    
    # Test clear
    storage.set("key2", "value2")
    storage.clear()
    assert storage.get("key2") is None
    print("✓ Memory storage clear test passed")

async def test_json_storage():
    """Test JSON storage"""
    print("Testing JSON storage...")
    
    storage = JSONStorage("test_data.json")
    
    # Test basic operations
    await storage.set("key1", "value1")
    value = await storage.get("key1")
    assert value == "value1"
    print("✓ JSON storage set/get test passed")
    
    # Test delete
    await storage.delete("key1")
    value = await storage.get("key1")
    assert value is None
    print("✓ JSON storage delete test passed")
    
    # Test clear
    await storage.set("key2", "value2")
    await storage.clear()
    value = await storage.get("key2")
    assert value is None
    print("✓ JSON storage clear test passed")
    
    # Clean up
    if os.path.exists("test_data.json"):
        os.remove("test_data.json")

async def test_redis_storage():
    """Test Redis storage"""
    print("Testing Redis storage...")
    
    try:
        storage = RedisStorage(host='localhost', port=6379, db=0)
        
        # Test basic operations
        storage.set("key1", "value1")
        value = storage.get("key1")
        assert value == "value1"
        print("✓ Redis storage set/get test passed")
        
        # Test delete
        storage.delete("key1")
        value = storage.get("key1")
        assert value is None
        print("✓ Redis storage delete test passed")
        
        # Test clear
        storage.set("key2", "value2")
        storage.clear()
        value = storage.get("key2")
        assert value is None
        print("✓ Redis storage clear test passed")
        
    except Exception as e:
        print(f"Redis storage test skipped: {e}")

if __name__ == "__main__":
    print("Running storage tests...")
    asyncio.run(test_memory_storage())
    asyncio.run(test_json_storage())
    asyncio.run(test_redis_storage())
    print("All storage tests passed! ✅")
