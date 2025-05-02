from sqlalchemy import (
    Column, String, Integer, ForeignKey, Boolean, Float, DateTime, Enum, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    is_guest = Column(Boolean, default=False)
    phone = Column(String, nullable=True)

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    number = Column(Integer)
    location = Column(String, nullable=True)
    restaurant = relationship("Restaurant")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    table_id = Column(Integer, ForeignKey("tables.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

class MenuCategory(Base):
    __tablename__ = "menu_categories"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    name = Column(String)
    description = Column(String, nullable=True)

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    category_id = Column(Integer, ForeignKey("menu_categories.id"))
    name = Column(String)
    description = Column(String, nullable=True)
    price = Column(Float)
    image_url = Column(String, nullable=True)
    available = Column(Boolean, default=True)
    # for simplicity we won’t model options in SQL here

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    special_instructions = Column(String, nullable=True)

class OrderStatusEnum(str, enum.Enum):
    pending = "pending"
    preparing = "preparing"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    table_id = Column(Integer, ForeignKey("tables.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.pending)
    subtotal = Column(Float)
    tax = Column(Float)
    total = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    items = relationship("OrderItem", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    payment_method = Column(String)
    amount = Column(Float)
    currency = Column(String, default="USD")
    payment_intent_id = Column(String)
    client_secret = Column(String)
    status = Column(String, default="pending")
    transaction_id = Column(String, nullable=True)

class SplitShare(Base):
    __tablename__ = "split_shares"
    id = Column(Integer, primary_key=True, index=True)
    bill_split_id = Column(Integer, ForeignKey("bill_splits.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    paid = Column(Boolean, default=False)

class BillSplit(Base):
    __tablename__ = "bill_splits"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    split_method = Column(String)  # "equal" or "custom"
    shares = relationship("SplitShare", cascade="all, delete-orphan")