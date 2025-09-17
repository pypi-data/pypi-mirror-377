from ..exceptions import APIException
from ..types import Message

async def send_message(client, chat_id, text, **kwargs):
    """Send a text message"""
    try:
        payload = {
            'chat_id': chat_id,
            'text': text,
            **kwargs
        }
        
        result = await client._make_request('sendMessage', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to send message: {e}")

async def send_photo(client, chat_id, photo, **kwargs):
    """Send a photo"""
    try:
        payload = {
            'chat_id': chat_id,
            'photo': photo,
            **kwargs
        }
        
        result = await client._make_request('sendPhoto', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to send photo: {e}")

async def send_document(client, chat_id, document, **kwargs):
    """Send a document"""
    try:
        payload = {
            'chat_id': chat_id,
            'document': document,
            **kwargs
        }
        
        result = await client._make_request('sendDocument', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to send document: {e}")

async def send_video(client, chat_id, video, **kwargs):
    """Send a video"""
    try:
        payload = {
            'chat_id': chat_id,
            'video': video,
            **kwargs
        }
        
        result = await client._make_request('sendVideo', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to send video: {e}")

async def send_audio(client, chat_id, audio, **kwargs):
    """Send an audio file"""
    try:
        payload = {
            'chat_id': chat_id,
            'audio': audio,
            **kwargs
        }
        
        result = await client._make_request('sendAudio', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to send audio: {e}")

async def send_voice(client, chat_id, voice, **kwargs):
    """Send a voice message"""
    try:
        payload = {
            'chat_id': chat_id,
            'voice': voice,
            **kwargs
        }
        
        result = await client._make_request('sendVoice', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to send voice: {e}")

async def send_location(client, chat_id, latitude, longitude, **kwargs):
    """Send a location"""
    try:
        payload = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            **kwargs
        }
        
        result = await client._make_request('sendLocation', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to send location: {e}")

async def send_contact(client, chat_id, phone_number, first_name, **kwargs):
    """Send a contact"""
    try:
        payload = {
            'chat_id': chat_id,
            'phone_number': phone_number,
            'first_name': first_name,
            **kwargs
        }
        
        result = await client._make_request('sendContact', payload)
        return Message.from_dict(result.get('result', {}))
    except Exception as e:
        raise APIException(f"Failed to send contact: {e}")
