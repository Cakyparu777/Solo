from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import schemas, crud, deps

router = APIRouter(prefix="/api/table", tags=["table"])

@router.get("/{restaurant_id}/{table_number}", response_model=schemas.TableInfoOut)
def get_table_info(
    restaurant_id: int,
    table_number: str,
    db: Session = Depends(deps.get_db)
):
    # Fetch the restaurant
    rest = crud.get_restaurant(db, restaurant_id)
    if not rest:
        raise HTTPException(404, "Restaurant not found")

    # Fetch the table
    tbl = crud.get_table(db, restaurant_id, table_number)
    if not tbl:
        raise HTTPException(404, "Table not found")

    # Fetch the active session
    sess = crud.get_active_session(db, tbl.id)

    # Return table information
    return schemas.TableInfoOut(
        restaurant_id=rest.id,
        restaurant_name=rest.name,
        table_id=tbl.id,
        table_number=tbl.number,
        table_location=tbl.location,
        current_session_id=(sess.id if sess else None)
    )

@router.post("/session", response_model=schemas.StartSessionOut)
def start_session(
    in_: schemas.StartSessionIn,
    db: Session = Depends(deps.get_db)
):
    # Create a new session
    sess = crud.create_session(db, in_.restaurant_id, in_.table_id, in_.user_id)

    # Return session details
    return schemas.StartSessionOut(
        session_id=sess.id,
        start_time=sess.start_time
    )