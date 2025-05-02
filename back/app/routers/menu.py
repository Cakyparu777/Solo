from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, deps, crud

router = APIRouter(tags=["menu"], prefix="/api/restaurants")

@router.get("/{restaurant_id}/menu", response_model=schemas.MenuOut)
def get_menu(
    restaurant_id: int,
    category_id: int = None,
    search: str = None,
    db: Session = Depends(deps.get_db)
):
    cats = crud.get_categories(db, restaurant_id, category_id, search)
    return {"categories": cats}

@router.get("/{restaurant_id}/featured", response_model=schemas.FeaturedOut)
def get_featured(
    restaurant_id: int,
    db: Session = Depends(deps.get_db)
):
    items = crud.get_featured(db, restaurant_id)
    return {"featured_items": items}