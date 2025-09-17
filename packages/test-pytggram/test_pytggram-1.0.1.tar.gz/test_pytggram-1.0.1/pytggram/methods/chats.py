from ..exceptions import APIException
from ..types import Chat, User

async def get_chat(client, chat_id):
    """Get information about a chat"""
    try:
        payload = {'chat_id': chat_id}
        result = await client._make_request('getChat', payload)
        return Chat.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to get chat: {e}")

async def get_chat_administrators(client, chat_id):
    """Get a list of administrators in a chat"""
    try:
        payload = {'chat_id': chat_id}
        result = await client._make_request('getChatAdministrators', payload)
        return [User.from_dict(admin) for admin in result.get('result', [])]
    except Exception as e:
        raise APIException(f"Failed to get chat administrators: {e}")

async def get_chat_members_count(client, chat_id):
    """Get the number of members in a chat"""
    try:
        payload = {'chat_id': chat_id}
        result = await client._make_request('getChatMembersCount', payload)
        return result.get('result', 0)
    except Exception as e:
        raise APIException(f"Failed to get chat members count: {e}")
