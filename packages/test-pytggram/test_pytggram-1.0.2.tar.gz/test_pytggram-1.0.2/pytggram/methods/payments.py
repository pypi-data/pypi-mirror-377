from ..exceptions import APIException

async def answer_pre_checkout_query(client, pre_checkout_query_id, ok, **kwargs):
    """Respond to a pre-checkout query"""
    try:
        payload = {
            'pre_checkout_query_id': pre_checkout_query_id,
            'ok': ok,
            **kwargs
        }
        
        result = await client._make_request('answerPreCheckoutQuery', payload)
        return result.get('ok', False)
    except Exception as e:
        raise APIException(f"Failed to answer pre-checkout query: {e}")

async def answer_shipping_query(client, shipping_query_id, ok, **kwargs):
    """Respond to a shipping query"""
    try:
        payload = {
            'shipping_query_id': shipping_query_id,
            'ok': ok,
            **kwargs
        }
        
        result = await client._make_request('answerShippingQuery', payload)
        return result.get('ok', False)
    except Exception as e:
        raise APIException(f"Failed to answer shipping query: {e}")
