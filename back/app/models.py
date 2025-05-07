import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean,
    DateTime, Enum, ForeignKey
)
from sqlalchemy.orm import relationship
from .database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# --- Enums ---
class RoleEnum(str, enum.Enum):
    admin = "admin"
    owner = "owner"
    employee = "employee"
    client = "client"

class OrderStatusEnum(str, enum.Enum):
    pending = "pending"
    preparing = "preparing"
    served = "served"
    paid = "paid"
    cancelled = "cancelled"

# --- Restaurant ---
class Restaurant(Base):
    __tablename__ = "restaurants"
    id                      = Column(Integer, primary_key=True, index=True)
    name                    = Column(String, nullable=False)
    owner_name              = Column(String, nullable=False)
    owner_email             = Column(String, nullable=False, unique=True)
    owner_phone             = Column(String)
    payment_status          = Column(Boolean, default=False)
    subscription_expires_at = Column(DateTime)
    created_at              = Column(DateTime, default=datetime.utcnow)

    # Relationships
    accounts = relationship("User", back_populates="restaurant", cascade="all,delete")
    tables   = relationship("Table", back_populates="restaurant", cascade="all,delete")
    menu     = relationship("MenuItem", back_populates="restaurant", cascade="all,delete")
    orders   = relationship("Order", back_populates="restaurant", cascade="all,delete")

# --- User ---
class User(Base):
    __tablename__ = "accounts"
    id             = Column(Integer, primary_key=True, index=True)
    restaurant_id  = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=True)
    email          = Column(String, nullable=False, unique=True)
    password_hash  = Column(String, nullable=False)
    name           = Column(String, nullable=False)
    phone          = Column(String)
    role           = Column(Enum(RoleEnum), nullable=False)
    created_at     = Column(DateTime, default=datetime.utcnow)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="accounts")
    sessions   = relationship("Session", back_populates="user", cascade="all,delete")
    orders     = relationship("Order", back_populates="client", cascade="all,delete")

# --- Table ---
class Table(Base):
    __tablename__ = "tables"
    id            = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    number        = Column(String, nullable=False)
    location      = Column(String)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="tables")
    sessions   = relationship("Session", back_populates="table", cascade="all,delete")
    orders     = relationship("Order", back_populates="table", cascade="all,delete")

# --- Session ---
class Session(Base):
    __tablename__ = "sessions"
    id             = Column(Integer, primary_key=True, index=True)
    restaurant_id  = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    table_id       = Column(Integer, ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)
    user_id        = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    start_time     = Column(DateTime, default=datetime.utcnow)
    end_time       = Column(DateTime)

    # Relationships
    restaurant = relationship("Restaurant")
    table      = relationship("Table", back_populates="sessions")
    user       = relationship("User", back_populates="sessions")
    orders     = relationship("Order", back_populates="session", cascade="all,delete")

# --- MenuItem ---
class MenuItem(Base):
    __tablename__ = "menu"
    id            = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name          = Column(String, nullable=False)
    description   = Column(Text)
    price         = Column(Numeric(7,2), nullable=False)
    category      = Column(String, nullable=False)
    available     = Column(Boolean, default=True)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu")
    order_items = relationship("OrderItem", back_populates="menu_item")

# --- Order ---
class Order(Base):
    __tablename__ = "orders"
    id             = Column(Integer, primary_key=True, index=True)
    restaurant_id  = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    table_id       = Column(Integer, ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)
    session_id     = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    client_id      = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    status         = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.pending, nullable=False)
    total_amount   = Column(Numeric(10,2), nullable=False)
    created_at     = Column(DateTime, default=datetime.utcnow)
    paid_at        = Column(DateTime)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="orders")
    table      = relationship("Table", back_populates="orders")
    session    = relationship("Session", back_populates="orders")
    client     = relationship("User", back_populates="orders")
    items      = relationship("OrderItem", back_populates="order", cascade="all,delete")

# --- OrderItem ---
class OrderItem(Base):
    __tablename__ = "order_items"
    id                   = Column(Integer, primary_key=True, index=True)
    order_id             = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_id              = Column(Integer, ForeignKey("menu.id", ondelete="RESTRICT"), nullable=False)
    quantity             = Column(Integer, nullable=False)
    unit_price           = Column(Numeric(8,2), nullable=False)
    special_instructions = Column(Text)

    # Relationships
    order      = relationship("Order", back_populates="items")
    menu_item  = relationship("MenuItem", back_populates="order_items")

# --- Payment ---
class Payment(Base):
    __tablename__ = "payments"
    id             = Column(Integer, primary_key=True, index=True)
    order_id       = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    payment_method = Column(String, nullable=False)
    amount         = Column(Numeric(10,2), nullable=False)
    currency       = Column(String, default="USD")
    intent_id      = Column(String, unique=True, index=True)
    status         = Column(String, default="pending")
    created_at     = Column(DateTime, default=datetime.utcnow)

# --- Auth ---
class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str]

class TokenOut(BaseModel):
    user_id: int
    token: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class GuestOut(BaseModel):
    guest_id: int
    token: str

# --- Restaurant / Table Session ---
class TableInfoOut(BaseModel):
    restaurant_id: int
    restaurant_name: str
    table_id: int
    table_number: str
    table_location: Optional[str]
    current_session_id: Optional[int]

class StartSessionIn(BaseModel):
    restaurant_id: int
    table_id: int
    user_id: Optional[int]

class StartSessionOut(BaseModel):
    session_id: int
    start_time: datetime

# --- Menu ---
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str]
    price: float
    category: str

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    category: Optional[str]
    available: Optional[bool]

class MenuItemOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category: str
    available: bool

    class Config:
        orm_mode = True

class CategoryOut(BaseModel):
    name: str
    items: List[MenuItemOut]

class MenuOut(BaseModel):
    categories: List[CategoryOut]

class FeaturedOut(BaseModel):
    featured_items: List[MenuItemOut]

# --- Orders ---
class OrderItemIn(BaseModel):
    item_id: int
    quantity: int
    special_instructions: Optional[str]

class CreateOrderIn(BaseModel):
    restaurant_id: int
    table_id: int
    session_id: int
    user_id: Optional[int]
    items: List[OrderItemIn]

class CreateOrderOut(BaseModel):
    order_id: int
    order_number: str
    estimated_time: int
    subtotal: float
    tax: float
    total: float
    created_at: datetime

class OrderStatusOut(BaseModel):
    order_id: int
    status: OrderStatusEnum
    estimated_completion_time: Optional[int]
    items: List[OrderItemIn]

class UpdateOrderIn(BaseModel):
    items: List[OrderItemIn]

class UpdateOrderOut(BaseModel):
    order_id: int
    subtotal: float
    tax: float
    total: float
    updated_at: datetime

# --- Payments ---
class CreatePaymentIn(BaseModel):
    order_id: int
    payment_method: str
    amount: float
    currency: Optional[str] = "USD"

class CreatePaymentOut(BaseModel):
    client_secret: str
    payment_intent_id: str

class ConfirmPaymentIn(BaseModel):
    payment_intent_id: str

class ConfirmPaymentOut(BaseModel):
    success: bool
    receipt_url: Optional[str]
    transaction_id: str

class SplitBillIn(BaseModel):
    order_id: int
    split_count: Optional[int]
    split_method: str  # "equal" or "custom"
    custom_split: Optional[List[OrderItemIn]]

class SplitBillOut(BaseModel):
    split_id: int
    split_options: List[dict]

# --- Admin ---
class ActiveOrderOut(BaseModel):
    order_id: int
    order_number: str
    table_number: str
    items: List[OrderItemIn]
    status: OrderStatusEnum
    created_at: datetime

class Pagination(BaseModel):
    total: int
    current_page: int
    total_pages: int

class GetActiveOrdersOut(BaseModel):
    orders: List[ActiveOrderOut]
    pagination: Pagination

class UpdateStatusIn(BaseModel):
    status: OrderStatusEnum
    estimated_completion_time: Optional[int]

class UpdateStatusOut(BaseModel):
    success: bool
    order_id: int
    status: OrderStatusEnum
    updated_at: datetime