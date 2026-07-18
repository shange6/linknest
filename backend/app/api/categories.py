from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth import require_admin
from app.models.category import Category
from app.models.user import User
from app.schemas.schemas import CategoryOut, CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["categories"])


def build_category_tree(categories: list[Category], parent_id: Optional[int] = None) -> list[dict]:
    """Recursively build category tree from flat list."""
    children = [c for c in categories if c.parent_id == parent_id]
    children.sort(key=lambda x: x.sort_order)
    result = []
    for child in children:
        node = {
            "id": child.id,
            "name": child.name,
            "slug": child.slug,
            "parent_id": child.parent_id,
            "sort_order": child.sort_order,
            "description": child.description,
            "updated_at": child.updated_at.isoformat() if child.updated_at else None,
            "children": build_category_tree(categories, child.id),
        }
        result.append(node)
    return result


@router.get("", response_model=list[dict])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.sort_order).all()
    return build_category_tree(categories)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/{category_id}/children", response_model=list[CategoryOut])
def get_category_children(category_id: int, db: Session = Depends(get_db)):
    children = db.query(Category).filter(Category.parent_id == category_id).order_by(Category.sort_order).all()
    return children


# --- Admin category management ---
@router.post("", response_model=CategoryOut, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = db.query(Category).filter(Category.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    if data.parent_id:
        parent = db.query(Category).filter(Category.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if data.slug is not None and data.slug != category.slug:
        existing = db.query(Category).filter(Category.slug == data.slug).first()
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    # Recursively delete all descendants
    _delete_children(db, category_id)
    db.delete(category)
    db.commit()
    return None


def _delete_children(db: Session, parent_id: int):
    children = db.query(Category).filter(Category.parent_id == parent_id).all()
    for child in children:
        _delete_children(db, child.id)
        db.delete(child)
