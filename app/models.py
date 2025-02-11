from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Text, Date, Numeric, Boolean, ARRAY
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Address(Base):
    __tablename__ = "addresses"
    
    address_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    street_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    is_primary = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="addresses")

class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    variations = relationship("ProductVariation", back_populates="product")
    reviews = relationship("Review", back_populates="product")

class ProductVariation(Base):
    __tablename__ = "product_variations"
    
    variation_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    sku = Column(String(50), unique=True)
    attributes = Column(JSON)
    price = Column(Numeric(10,2))
    image_urls = Column(ARRAY(String))
    available_from = Column(Date)
    available_to = Column(Date)
    
    product = relationship("Product", back_populates="variations")
    inventory = relationship("Inventory", back_populates="variation")

class Inventory(Base):
    __tablename__ = "inventory"
    
    inventory_id = Column(Integer, primary_key=True, index=True)
    variation_id = Column(Integer, ForeignKey("product_variations.variation_id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"))
    quantity = Column(Integer)
    low_stock_threshold = Column(Integer, default=10)
    
    variation = relationship("ProductVariation", back_populates="inventory")

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    shipping_address_id = Column(Integer, ForeignKey("addresses.address_id"))
    status = Column(Enum('pending', 'processing', 'shipped', 'delivered', 'cancelled', name='order_status'))
    total_amount = Column(Numeric(12,2))
    order_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    variation_id = Column(Integer, ForeignKey("product_variations.variation_id"))
    quantity = Column(Integer)
    price_at_purchase = Column(Numeric(10,2))
    
    order = relationship("Order", back_populates="items")

class Review(Base):
    __tablename__ = "reviews"
    
    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")
    product = relationship("Product", back_populates="reviews")