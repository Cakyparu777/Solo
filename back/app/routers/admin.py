from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, deps, crud

router = APIRouter(tags=["admin"], prefix="/api/admin")

@router.get("/restaurants/{restaurant_id}/orders", response_model=schemas.GetActiveOrdersOut)
def list_orders(
    restaurant_id: int,
    status: str = None,
    limit: int = 20,
    page: int = 1,
    db: Session = Depends(deps.get_db)
):
    return crud.list_orders(db, restaurant_id, status, limit, page)

@router.put("/orders/{order_id}/status", response_model=schemas.UpdateStatusOut)
def update_status(
    order_id: int,
    in_: schemas.UpdateStatusIn,
    db: Session = Depends(deps.get_db)
):
    return crud.change_order_status(db, order_id, in_.status)