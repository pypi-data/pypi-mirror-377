from ..exceptions import APIException
from ..types import Message

async def forward_message(client, chat_id, from_chat_id, message_id, **kwargs):
    """Forward a message"""
    try:
        payload = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id,
            **kwargs
        }
        
        result = await client._make_request('forwardMessage', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to forward message: {e}")

async def copy_message(client, chat_id, from_chat_id, message_id, **kwargs):
    """Copy a message"""
    try:
        payload = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id,
            **kwargs
        }
        
        result = await client._make_request('copyMessage', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to copy message: {e}")

async def delete_message(client, chat_id, message_id):
    """Delete a message"""
    try:
        payload = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        
        result = await client._make_request('deleteMessage', payload)
        return result.get('ok', False)
    except Exception as e:
        raise APIException(f"Failed to delete message: {e}")

async def edit_message_text(client, text, **kwargs):
    """Edit message text"""
    try:
        payload = {
            'text': text,
            **kwargs
        }
        
        result = await client._make_request('editMessageText', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to edit message text: {e}")

async def edit_message_caption(client, caption, **kwargs):
    """Edit message caption"""
    try:
        payload = {
            'caption': caption,
            **kwargs
        }
        
        result = await client._make_request('editMessageCaption', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to edit message caption: {e}")

async def edit_message_media(client, media, **kwargs):
    """Edit message media"""
    try:
        payload = {
            'media': media,
            **kwargs
        }
        
        result = await client._make_request('editMessageMedia', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to edit message media: {e}")

async def edit_message_reply_markup(client, reply_markup, **kwargs):
    """Edit message reply markup"""
    try:
        payload = {
            'reply_markup': reply_markup,
            **kwargs
        }
        
        result = await client._make_request('editMessageReplyMarkup', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to edit message reply markup: {e}")
