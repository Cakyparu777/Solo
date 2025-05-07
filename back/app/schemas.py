from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import OrderStatusEnum

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

# --- Table ---
class TableInfoOut(BaseModel):
    restaurant_id: int
    restaurant_name: str
    table_number: int
    table_location: Optional[str]
    current_session_id: Optional[int]

class StartSessionIn(BaseModel):
    restaurant_id: int
    table_id: int
    user_id: int

class StartSessionOut(BaseModel):
    session_id: int
    start_time: datetime

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    available: bool

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    category: Optional[str]
    available: Optional[bool]

class MenuItemOut(BaseModel):
    id:          int
    name:        str
    description: Optional[str]
    price:       float
    category:    str
    available:   bool

    class Config:
        orm_mode = True

class CategoryOut(BaseModel):
    name: str
    items: List[MenuItemOut]

class MenuOut(BaseModel):
    categories: List[CategoryOut]

class FeaturedOut(BaseModel):
    featured_items: List[MenuItemOut]

# --- Order ---
class OrderItemIn(BaseModel):
    item_id: int
    quantity: int
    special_instructions: Optional[str]

class CreateOrderIn(BaseModel):
    restaurant_id: int
    table_id: int
    session_id: int
    user_id: int
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
    estimated_completion_time: datetime
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
    receipt_url: str
    transaction_id: str

class SplitBillIn(BaseModel):
    order_id: int
    split_count: Optional[int]
    split_method: str  # "equal" or "custom"
    custom_split: Optional[List[OrderItemIn]]  # reuse OrderItemIn for simplicity

class SplitBillOut(BaseModel):
    split_id: int
    split_options: List[dict]

# --- Admin ---
class ActiveOrderOut(BaseModel):
    order_id: int
    order_number: str
    table_number: int
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
    estimated_completion_time: Optional[int]  # minutes

class UpdateStatusOut(BaseModel):
    success: bool
    order_id: int
    status: OrderStatusEnum
    updated_at: datetime