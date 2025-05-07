from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
from .. import schemas, crud, deps
from ..models import RoleEnum

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=schemas.TokenOut)
def register(
    in_: schemas.RegisterIn,
    db: Session = Depends(deps.get_db)
):
    if crud.get_user_by_email(db, in_.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    user = crud.create_user(
        db,
        name=in_.name,
        email=in_.email,
        password=in_.password,
        phone=in_.phone,
        role=RoleEnum.client
    )
    token = crud.create_jwt(user.id)
    return {"user_id": user.id, "token": token}

@router.post("/login", response_model=schemas.TokenOut)
def login(
    in_: schemas.LoginIn,
    db: Session = Depends(deps.get_db)
):
    user = crud.authenticate_user(db, in_.email, in_.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = crud.create_jwt(user.id)
    return {"user_id": user.id, "token": token}

@router.post("/guest", response_model=schemas.GuestOut)
def guest(db: Session = Depends(deps.get_db)):
    # Create a guest user
    user = crud.create_user(
        db,
        name="Guest",
        email=f"guest_{datetime.utcnow().timestamp()}@qrcode",
        password="",
        phone=None,
        role=RoleEnum.client
    )
    token = crud.create_jwt(user.id)
    return {"guest_id": user.id, "token": token}