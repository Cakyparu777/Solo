from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, deps, crud

router = APIRouter(tags=["payment"], prefix="/api/payments")

@router.post("/intent", response_model=schemas.CreatePaymentOut)
def create_intent(in_: schemas.CreatePaymentIn, db: Session = Depends(deps.get_db)):
    return crud.create_payment(db, in_)

@router.post("/confirm", response_model=schemas.ConfirmPaymentOut)
def confirm(in_: schemas.ConfirmPaymentIn, db: Session = Depends(deps.get_db)):
    return crud.confirm_payment(db, in_.payment_intent_id)

@router.post("/split", response_model=schemas.SplitBillOut)
def split(in_: schemas.SplitBillIn, db: Session = Depends(deps.get_db)):
    return crud.split_bill(db, in_)