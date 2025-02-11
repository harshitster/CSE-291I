from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, conint
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class PaymentMethod(str, Enum):
    CREDIT_CARD = 'credit_card'
    PAYPAL = 'paypal'
    BANK_TRANSFER = 'bank_transfer'

class PaymentStatus(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        orm_mode = True

# Address Schemas
class AddressBase(BaseModel):
    street_address: str
    city: str
    state: Optional[str]
    postal_code: Optional[str]
    country: str
    is_primary: bool = False

class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    address_id: int
    user_id: int

    class Config:
        orm_mode = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    category_id: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Product Variation Schemas
class ProductVariationBase(BaseModel):
    sku: str
    attributes: dict
    price: float
    image_urls: List[str]
    available_from: date
    available_to: Optional[date]

class ProductVariationCreate(ProductVariationBase):
    pass

class ProductVariation(ProductVariationBase):
    variation_id: int
    product_id: int

    class Config:
        orm_mode = True

# Order Schemas
class OrderBase(BaseModel):
    shipping_address_id: int
    status: OrderStatus = OrderStatus.PENDING
    total_amount: float

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    order_id: int
    user_id: int
    order_date: datetime

    class Config:
        orm_mode = True

# Inventory Schemas
class InventoryBase(BaseModel):
    quantity: int
    low_stock_threshold: int = 10

class InventoryUpdate(InventoryBase):
    pass

class Inventory(InventoryBase):
    inventory_id: int
    variation_id: int
    warehouse_id: int

    class Config:
        orm_mode = True

class ReviewBase(BaseModel):
    # rating: conint()
    comment: Optional[str]

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    review_id: int
    user_id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True