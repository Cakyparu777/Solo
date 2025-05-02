from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, deps, crud

router = APIRouter(tags=["order"], prefix="/api/orders")

@router.post("", response_model=schemas.CreateOrderOut)
def create_order(in_: schemas.CreateOrderIn, db: Session = Depends(deps.get_db)):
    return crud.create_order(db, in_)

@router.get("/{order_id}", response_model=schemas.OrderStatusOut)
def get_status(order_id: int, db: Session = Depends(deps.get_db)):
    o = crud.get_order(db, order_id)
    if not o: raise HTTPException(404, "Order not found")
    return o

@router.put("/{order_id}", response_model=schemas.UpdateOrderOut)
def update(order_id: int, in_: schemas.UpdateOrderIn, db: Session = Depends(deps.get_db)):
    return crud.update_order(db, order_id, in_.items)