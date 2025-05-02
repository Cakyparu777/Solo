from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
import os
from . import models, schemas

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id==user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email==email).first()

def create_user(db: Session, name, email, password, phone, is_guest=False):
    user = models.User(
        name=name, email=email,
        password_hash=pwd_ctx.hash(password) if password else None,
        phone=phone, is_guest=is_guest
    )
    db.add(user); db.commit(); db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not pwd_ctx.verify(password, user.password_hash):
        return None
    return user

def create_jwt(user_id: int):
    to_encode = {"user_id": user_id}
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# --- Table & Session ---
def get_restaurant(db: Session, rid: int): ...
def get_table(db: Session, rid: int, number: int): ...
def create_session(db: Session, restaurant_id, table_id, user_id): ...
def get_active_session(db: Session, table_id): ...

# --- Menu ---
def get_categories(db: Session, restaurant_id, category_id=None, search=None): ...
def get_featured(db: Session, restaurant_id): ...

# --- Orders ---
def create_order(db: Session, data: schemas.CreateOrderIn): ...
def get_order(db: Session, oid: int): ...
def update_order(db: Session, oid: int, items): ...

# --- Payments ---
def create_payment(db: Session, data: schemas.CreatePaymentIn): ...
def confirm_payment(db: Session, intent_id: str): ...
def split_bill(db: Session, data: schemas.SplitBillIn): ...

# --- Admin ---
def list_orders(db: Session, restaurant_id, status, limit, page): ...
def change_order_status(db: Session, oid: int, status): ...