from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import schemas, crud, deps

router = APIRouter(prefix="/api/orders", tags=["order"])

@router.post("", response_model=schemas.CreateOrderOut)
def create_order(
    in_: schemas.CreateOrderIn,
    db: Session = Depends(deps.get_db)
):
    try:
        # Attempt to create an order
        return crud.create_order(db, in_)
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(400, str(e))

@router.get("/{order_id}", response_model=schemas.OrderStatusOut)
def get_order(order_id: int, db: Session = Depends(deps.get_db)):
    # Fetch the order by ID
    ord = crud.get_order(db, order_id)
    if not ord:
        # Raise 404 if the order is not found
        raise HTTPException(404, "Order not found")
    return ord

@router.put("/{order_id}", response_model=schemas.UpdateOrderOut)
def update_order(
    order_id: int,
    in_: schemas.UpdateOrderIn,
    db: Session = Depends(deps.get_db)
):
    # Attempt to update the order
    out = crud.update_order(db, order_id, in_.items)
    if not out:
        # Raise 404 if the order is not found
        raise HTTPException(404, "Order not found")
    return out