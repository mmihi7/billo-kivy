from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean, JSON, DateTime, Text, Numeric
from sqlalchemy.orm import relationship
from .base import Base, BaseModel
from datetime import datetime
import enum

class UserRole(enum.Enum):
    CUSTOMER = "customer"
    WAITER = "waiter"
    ADMIN = "admin"

class User(Base, BaseModel):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)  # Supabase Auth ID
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, unique=True)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserRole.CUSTOMER.value)
    avatar_url = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    customer_tabs = relationship("Tab", back_populates="customer", foreign_keys="[Tab.customer_id]")
    waiter_orders = relationship("Order", back_populates="waiter")

class Restaurant(Base, BaseModel):
    __tablename__ = 'restaurants'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    county = Column(String, nullable=False)
    location = Column(String, nullable=False)
    business_hours = Column(JSON)
    qr_code_url = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    menu_items = relationship("MenuItem", back_populates="restaurant")
    tabs = relationship("Tab", back_populates="restaurant")
    waiters = relationship("Waiter", back_populates="restaurant")

class Waiter(Base, BaseModel):
    __tablename__ = 'waiters'
    
    id = Column(String, primary_key=True)
    restaurant_id = Column(String, ForeignKey('restaurants.id'), nullable=False)
    name = Column(String, nullable=False)
    pin = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="waiters")
    orders = relationship("Order", back_populates="waiter")

class Tab(Base, BaseModel):
    __tablename__ = 'tabs'
    
    id = Column(String, primary_key=True)
    restaurant_id = Column(String, ForeignKey('restaurants.id'), nullable=False)
    customer_id = Column(String, ForeignKey('users.id'), nullable=False)
    tab_number = Column(Integer, nullable=False)
    status = Column(String, default="open")  # open, closed, paid, cancelled
    notes = Column(Text)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="tabs")
    customer = relationship("User", back_populates="customer_tabs", foreign_keys=[customer_id])
    orders = relationship("Order", back_populates="tab")
    payments = relationship("Payment", back_populates="tab")
    messages = relationship("Message", back_populates="tab")

class MenuItem(Base, BaseModel):
    __tablename__ = 'menu_items'
    
    id = Column(String, primary_key=True)
    restaurant_id = Column(String, ForeignKey('restaurants.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String)
    is_available = Column(Boolean, default=True)
    image_url = Column(String)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")

class Order(Base, BaseModel):
    __tablename__ = 'orders'
    
    class Status(enum.Enum):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        PREPARING = "preparing"
        READY = "ready"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"
    
    id = Column(String, primary_key=True)
    tab_id = Column(String, ForeignKey('tabs.id'), nullable=False)
    waiter_id = Column(String, ForeignKey('waiters.id'))
    status = Column(String, default=Status.PENDING.value)
    notes = Column(Text)
    
    # Relationships
    tab = relationship("Tab", back_populates="orders")
    waiter = relationship("Waiter", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base, BaseModel):
    __tablename__ = 'order_items'
    
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey('orders.id'), nullable=False)
    menu_item_id = Column(String, ForeignKey('menu_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")

class Payment(Base, BaseModel):
    __tablename__ = 'payments'
    
    class Method(enum.Enum):
        CASH = "cash"
        MPESA = "mpesa"
        AIRTEL_MONEY = "airtel_money"
    
    id = Column(String, primary_key=True)
    tab_id = Column(String, ForeignKey('tabs.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, completed, failed
    reference = Column(String)  # Payment reference number
    phone_number = Column(String)  # For mobile money payments
    
    # Relationships
    tab = relationship("Tab", back_populates="payments")

class Message(Base, BaseModel):
    __tablename__ = 'messages'
    
    class SenderType(enum.Enum):
        CUSTOMER = "customer"
        WAITER = "waiter"
    
    id = Column(String, primary_key=True)
    tab_id = Column(String, ForeignKey('tabs.id'), nullable=False)
    sender_type = Column(String, nullable=False)  # customer or waiter
    sender_id = Column(String, nullable=False)  # user_id or waiter_id
    message = Column(Text, nullable=False)
    
    # Relationships
    tab = relationship("Tab", back_populates="messages")
