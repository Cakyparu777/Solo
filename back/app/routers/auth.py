from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud import (
    get_user_by_email, create_user, authenticate_user, create_jwt
)
import app.schemas as schemas
import app.deps as deps

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=schemas.TokenOut)
def register(in_: schemas.RegisterIn, db: Session = Depends(deps.get_db)):
    if get_user_by_email(db, in_.email):
        raise HTTPException(400, "Email already registered")
    user = create_user(db, in_.name, in_.email, in_.password, in_.phone)
    token = create_jwt(user.id)
    return {"user_id": user.id, "token": token}

@router.post("/login", response_model=schemas.TokenOut)
def login(form: schemas.LoginIn, db: Session = Depends(deps.get_db)):
    user = authenticate_user(db, form.email, form.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid creds")
    token = create_jwt(user.id)
    return {"user_id": user.id, "token": token}

@router.post("/guest", response_model=schemas.GuestOut)
def guest(db: Session = Depends(deps.get_db)):
    guest = create_user(db, name=None, email=None, password=None, phone=None, is_guest=True)
    token = create_jwt(guest.id)
    return {"guest_id": guest.id, "token": token}