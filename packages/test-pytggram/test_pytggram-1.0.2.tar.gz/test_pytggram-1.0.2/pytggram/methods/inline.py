from ..exceptions import APIException

async def answer_inline_query(client, inline_query_id, results, **kwargs):
    """Send answers to an inline query"""
    try:
        payload = {
            'inline_query_id': inline_query_id,
            'results': results,
            **kwargs
        }
        
        result = await client._make_request('answerInlineQuery', payload)
        return result.get('ok', False)
    except Exception as e:
        raise APIException(f"Failed to answer inline query: {e}")
