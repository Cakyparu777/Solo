from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import schemas, crud, deps

router = APIRouter(prefix="/api/payments", tags=["payment"])

@router.post("", response_model=schemas.CreatePaymentOut)
def create_payment(
    in_: schemas.CreatePaymentIn,
    db: Session = Depends(deps.get_db)
):
    # Create a payment intent
    try:
        return crud.create_payment(db, in_)
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/confirm", response_model=schemas.ConfirmPaymentOut)
def confirm_payment(
    in_: schemas.ConfirmPaymentIn,
    db: Session = Depends(deps.get_db)
):
    # Confirm the payment intent
    try:
        return crud.confirm_payment(db, in_.payment_intent_id)
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/split", response_model=schemas.SplitBillOut)
def split_bill(
    in_: schemas.SplitBillIn,
    db: Session = Depends(deps.get_db)
):
    # Split the bill
    try:
        return crud.split_bill(db, in_)
    except Exception as e:
        raise HTTPException(400, str(e))