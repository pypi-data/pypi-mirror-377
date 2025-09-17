from ..exceptions import APIException
from ..types import User

async def get_me(client):
    """A simple method for testing your bot's auth token."""
    try:
        result = await client._make_request('getMe')
        return User.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to get bot info: {e}")
