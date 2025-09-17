from dataclasses import dataclass
from typing import Optional, Dict, Any
from .user import User

@dataclass
class ShippingAddress:
    """This object represents a shipping address"""
    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str

@dataclass
class OrderInfo:
    """This object represents information about an order"""
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[ShippingAddress] = None

@dataclass
class PreCheckoutQuery:
    """This object contains information about an incoming pre-checkout query"""
    id: str
    from_user: User
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PreCheckoutQuery':
        """Create a PreCheckoutQuery object from API response"""
        from_user = User.from_dict(data.get('from')) if data.get('from') else None
        
        # Parse order info if available
        order_info = None
        if data.get('order_info'):
            order_info_data = data.get('order_info')
            shipping_address = None
            if order_info_data.get('shipping_address'):
                addr_data = order_info_data.get('shipping_address')
                shipping_address = ShippingAddress(
                    country_code=addr_data.get('country_code'),
                    state=addr_data.get('state'),
                    city=addr_data.get('city'),
                    street_line1=addr_data.get('street_line1'),
                    street_line2=addr_data.get('street_line2'),
                    post_code=addr_data.get('post_code')
                )
            
            order_info = OrderInfo(
                name=order_info_data.get('name'),
                phone_number=order_info_data.get('phone_number'),
                email=order_info_data.get('email'),
                shipping_address=shipping_address
            )
        
        return cls(
            id=data.get('id'),
            from_user=from_user,
            currency=data.get('currency'),
            total_amount=data.get('total_amount'),
            invoice_payload=data.get('invoice_payload'),
            shipping_option_id=data.get('shipping_option_id'),
            order_info=order_info
        )

@dataclass
class ShippingQuery:
    """This object contains information about an incoming shipping query"""
    id: str
    from_user: User
    invoice_payload: str
    shipping_address: ShippingAddress
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ShippingQuery':
        """Create a ShippingQuery object from API response"""
        from_user = User.from_dict(data.get('from')) if data.get('from') else None
        
        # Parse shipping address
        addr_data = data.get('shipping_address')
        shipping_address = ShippingAddress(
            country_code=addr_data.get('country_code'),
            state=addr_data.get('state'),
            city=addr_data.get('city'),
            street_line1=addr_data.get('street_line1'),
            street_line2=addr_data.get('street_line2'),
            post_code=addr_data.get('post_code')
        )
        
        return cls(
            id=data.get('id'),
            from_user=from_user,
            invoice_payload=data.get('invoice_payload'),
            shipping_address=shipping_address
        )
