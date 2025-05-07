from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext
from jose import jwt
import os
from datetime import datetime
from . import models, schemas

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME")
TAX_RATE = 0.10  # 10%

# --- Auth ---
def get_user(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, name, email, password, phone, role, restaurant_id=None):
    user = models.User(
        name=name,
        email=email,
        password_hash=pwd_ctx.hash(password),
        phone=phone,
        role=role,
        restaurant_id=restaurant_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user or not pwd_ctx.verify(password, user.password_hash):
        return None
    return user

def create_jwt(user_id: int) -> str:
    to_encode = {"user_id": user_id, "exp": datetime.utcnow().timestamp() + 3600 * 24}
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# --- Menu Management ---
def get_menu_items(db: Session, restaurant_id: int):
    return db.query(models.MenuItem).filter(models.MenuItem.restaurant_id == restaurant_id).all()

def get_menu_item(db: Session, item_id: int):
    return db.query(models.MenuItem).get(item_id)

def get_categories(
    db: Session,
    restaurant_id: int,
    category: Optional[str] = None,
    search: Optional[str] = None
) -> List[schemas.CategoryOut]:
    q = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.restaurant_id == restaurant_id,
                models.MenuItem.available == True)
    )
    if category:
        q = q.filter(models.MenuItem.category == category)
    if search:
        q = q.filter(models.MenuItem.name.ilike(f"%{search}%"))
    items = q.all()

    from collections import defaultdict
    groups = defaultdict(list)
    for it in items:
        groups[it.category].append(it)

    out: List[schemas.CategoryOut] = []
    for cat_name, its in groups.items():
        out.append(schemas.CategoryOut(
            name=cat_name,
            items=[schemas.MenuItemOut.from_orm(i) for i in its]
        ))
    return out

def get_featured(
    db: Session,
    restaurant_id: int,
    limit: int = 5
) -> List[schemas.MenuItemOut]:
    items = (
        db.query(models.MenuItem)
        .filter(
            models.MenuItem.restaurant_id == restaurant_id,
            models.MenuItem.category == "popular",
            models.MenuItem.available == True
        )
        .limit(limit)
        .all()
    )
    return [schemas.MenuItemOut.from_orm(i) for i in items]

def create_menu_item(
    db: Session,
    restaurant_id: int,
    data: schemas.MenuItemCreate
) -> models.MenuItem:
    item = models.MenuItem(
        restaurant_id=restaurant_id,
        name=data.name,
        description=data.description,
        price=data.price,
        category=data.category,
        available=True
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def update_menu_item(
    db: Session,
    item: models.MenuItem,
    data: schemas.MenuItemUpdate
) -> models.MenuItem:
    for k, v in data.dict(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

def delete_menu_item(db: Session, item_id: int):
    db.query(models.MenuItem).filter(models.MenuItem.id == item_id).delete()
    db.commit()

# --- Table & Session ---
def get_restaurant(db: Session, rid: int) -> models.Restaurant:
    return db.query(models.Restaurant).get(rid)

def get_table(db: Session, rid: int, number: str) -> models.Table:
    return (
        db.query(models.Table)
        .filter(
            models.Table.restaurant_id == rid,
            models.Table.number == number
        )
        .first()
    )

def create_session(db: Session, restaurant_id: int, table_id: int, user_id: Optional[int]):
    session = models.Session(
        restaurant_id=restaurant_id,
        table_id=table_id,
        user_id=user_id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_active_session(db: Session, table_id: int) -> Optional[models.Session]:
    return (
        db.query(models.Session)
        .filter(
            models.Session.table_id == table_id,
            models.Session.end_time == None
        )
        .order_by(models.Session.start_time.desc())
        .first()
    )

# --- Orders ---
def create_order(db: Session, data: schemas.CreateOrderIn) -> schemas.CreateOrderOut:
    # Calculate subtotal
    subtotal = 0
    for oi in data.items:
        mi = db.query(models.MenuItem).get(oi.item_id)
        if not mi or not mi.available:
            raise ValueError(f"MenuItem {oi.item_id} not available")
        subtotal += float(mi.price) * oi.quantity

    tax = round(subtotal * TAX_RATE, 2)
    total = round(subtotal + tax, 2)

    order = models.Order(
        restaurant_id=data.restaurant_id,
        table_id=data.table_id,
        session_id=data.session_id,
        client_id=data.user_id,
        status=models.OrderStatusEnum.pending,
        total_amount=total
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create line items
    for oi in data.items:
        mi = db.query(models.MenuItem).get(oi.item_id)
        oi_rec = models.OrderItem(
            order_id=order.id,
            menu_id=oi.item_id,
            quantity=oi.quantity,
            unit_price=mi.price,
            special_instructions=oi.special_instructions
        )
        db.add(oi_rec)
    db.commit()

    return schemas.CreateOrderOut(
        order_id=order.id,
        order_number=f"#{order.id:06d}",
        estimated_time=15,
        subtotal=subtotal,
        tax=tax,
        total=total,
        created_at=order.created_at
    )

def get_order(db: Session, oid: int) -> schemas.OrderStatusOut:
    order = db.query(models.Order).get(oid)
    if not order:
        return None
    items = [
        schemas.OrderItemIn(
            item_id=oi.menu_id,
            quantity=oi.quantity,
            special_instructions=oi.special_instructions
        )
        for oi in order.items
    ]
    return schemas.OrderStatusOut(
        order_id=order.id,
        status=order.status,
        estimated_completion_time=None,
        items=items
    )

# --- Payments ---
def create_payment(db: Session, data: schemas.CreatePaymentIn): ...
def confirm_payment(db: Session, intent_id: str): ...
def split_bill(db: Session, data: schemas.SplitBillIn): ...

# --- Admin ---
def list_orders(
    db: Session,
    restaurant_id: Optional[int],
    status: Optional[schemas.OrderStatusEnum],
    limit: int,
    page: int
) -> Tuple[List[schemas.ActiveOrderOut], schemas.Pagination]:
    q = db.query(models.Order)
    if restaurant_id:
        q = q.filter(models.Order.restaurant_id == restaurant_id)
    if status:
        q = q.filter(models.Order.status == status)

    total = q.count()
    pages = (total + limit - 1) // limit
    offs = (page - 1) * limit

    orders = q.order_by(models.Order.created_at.desc()).offset(offs).limit(limit).all()
    out = []
    for o in orders:
        items = [schemas.OrderItemIn(
            item_id=i.menu_id,
            quantity=i.quantity,
            special_instructions=i.special_instructions
        ) for i in o.items]
        out.append(schemas.ActiveOrderOut(
            order_id=o.id,
            order_number=f"#{o.id:06d}",
            table_number=o.table.number,
            items=items,
            status=o.status,
            created_at=o.created_at
        ))
    return out, schemas.Pagination(
        total=total, current_page=page, total_pages=pages
    )

def change_order_status(db: Session, oid: int, status): ...