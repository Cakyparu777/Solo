from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, deps, models

router = APIRouter(prefix="/api/admin/menu", tags=["admin_menu"])

@router.get("/{restaurant_id}", response_model=List[schemas.MenuItemOut])
def list_menu(
    restaurant_id: int,
    db: Session = Depends(deps.get_db)
):
    # Fetch all menu items for the restaurant
    items = crud.get_menu_items(db, restaurant_id)
    return [schemas.MenuItemOut.from_orm(i) for i in items]

@router.post("/{restaurant_id}", response_model=schemas.MenuItemOut, status_code=201)
def create_item(
    restaurant_id: int,
    in_: schemas.MenuItemCreate,
    db: Session = Depends(deps.get_db)
):
    # Create a new menu item for the restaurant
    return crud.create_menu_item(db, restaurant_id, in_)

@router.put("/{restaurant_id}/{item_id}", response_model=schemas.MenuItemOut)
def update_item(
    restaurant_id: int,
    item_id: int,
    in_: schemas.MenuItemUpdate,
    db: Session = Depends(deps.get_db)
):
    # Fetch the menu item by ID
    item = db.query(models.MenuItem).get(item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(404, "Not found")
    # Update the menu item
    return crud.update_menu_item(db, item, in_)

@router.delete("/{restaurant_id}/{item_id}", status_code=204)
def delete_item(
    restaurant_id: int,
    item_id: int,
    db: Session = Depends(deps.get_db)
):
    # Fetch the menu item by ID
    item = db.query(models.MenuItem).get(item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(404, "Not found")
    # Delete the menu item
    crud.delete_menu_item(db, item_id)