from typing import List, Dict, Any

async def create_mongodb_indexes(db, collections: List[str] = None):
    """Create indexes for MongoDB collections"""
    indexes = {
        'users': [
            [('user_id', 1)],  # Primary index
            [('username', 1)],  # Search by username
        ],
        'chats': [
            [('chat_id', 1)],  # Primary index
            [('type', 1)],  # Search by chat type
        ],
        'messages': [
            [('message_id', 1)],  # Primary index
            [('chat_id', 1), ('message_id', 1)],  # Compound index
            [('date', 1)],  # TTL index for auto-expiry
        ],
        'user_data': [
            [('user_id', 1), ('key', 1)],  # Compound primary index
        ],
        'chat_data': [
            [('chat_id', 1), ('key', 1)],  # Compound primary index
        ]
    }
    
    collections_to_index = collections or indexes.keys()
    
    for collection in collections_to_index:
        if collection in indexes:
            for index_keys in indexes[collection]:
                await db[collection].create_index(index_keys)
    
    return True

async def mongodb_bulk_operations(db, collection: str, operations: List[Dict[str, Any]]):
    """Perform bulk operations on MongoDB"""
    try:
        result = await db[collection].bulk_write(operations)
        return result
    except Exception as e:
        raise Exception(f"Bulk operation failed: {e}")
