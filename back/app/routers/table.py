from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, deps, crud

router = APIRouter(tags=["table"], prefix="/api/table")

@router.get("/info", response_model=schemas.TableInfoOut)
def get_info(qrCode: str, db: Session = Depends(deps.get_db)):
    # stub: assume qrCode = "{restaurant_id}|{table_number}"
    rid, tbl = qrCode.split("|")
    restaurant = crud.get_restaurant(db, int(rid))
    if not restaurant: raise HTTPException(404, "No restaurant")
    table = crud.get_table(db, restaurant.id, int(tbl))
    if not table: raise HTTPException(404, "No table")
    session = crud.get_active_session(db, table.id)
    return {
        "restaurant_id": restaurant.id,
        "restaurant_name": restaurant.name,
        "table_number": table.number,
        "table_location": table.location,
        "current_session_id": session.id if session else None
    }

@router.post("/session", response_model=schemas.StartSessionOut)
def start_session(in_: schemas.StartSessionIn, db: Session = Depends(deps.get_db)):
    s = crud.create_session(db, in_.restaurant_id, in_.table_id, in_.user_id)
    return {"session_id": s.id, "start_time": s.started_at}