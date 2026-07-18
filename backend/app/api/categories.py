from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth import require_admin, get_current_user
from app.models.category import Category
from app.models.user import User
from app.schemas.schemas import CategoryOut, CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["categories"])


def check_category_permission(db: Session, category: Category, user: User) -> bool:
    """Check recursively if the user is a manager of this category or any ancestor category."""
    if user.role == "admin":
        return True
    current = category
    while current:
        if user in current.managers:
            return True
        if current.parent_id:
            current = db.query(Category).filter(Category.id == current.parent_id).first()
        else:
            break
    return False


def build_category_tree(categories: list[Category], parent_id: Optional[int] = None) -> list[dict]:
    """Recursively build category tree from flat list."""
    children = [c for c in categories if c.parent_id == parent_id]
    children.sort(key=lambda x: (x.sort_zh if x.sort_zh is not None else 99999, x.sort_en if x.sort_en is not None else 99999))
    result = []
    for child in children:
        node = {
            "id": child.id,
            "name_zh": child.name_zh,
            "name_en": child.name_en,
            "slug": child.slug,
            "parent_id": child.parent_id,
            "sort_zh": child.sort_zh,
            "sort_en": child.sort_en,
            "status": child.status,
            "desc_zh": child.desc_zh,
            "desc_en": child.desc_en,
            "updated_at": child.updated_at.isoformat() if child.updated_at else None,
            "managers": [{"id": m.id, "username": m.username, "email": m.email} for m in child.managers],
            "children": build_category_tree(categories, child.id),
        }
        result.append(node)
    return result


@router.get("", response_model=list[dict])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.sort_zh, Category.sort_en).all()
    return build_category_tree(categories)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/{category_id}/children", response_model=list[CategoryOut])
def get_category_children(category_id: int, db: Session = Depends(get_db)):
    children = db.query(Category).filter(Category.parent_id == category_id).order_by(Category.sort_zh, Category.sort_en).all()
    return children


# --- Category management with permissions ---
@router.post("", response_model=CategoryOut, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Category).filter(Category.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    # Permission check
    if not data.parent_id:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can create root categories")
    else:
        parent = db.query(Category).filter(Category.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")
        if not check_category_permission(db, parent, current_user):
            raise HTTPException(status_code=403, detail="Permission denied to manage this parent category")

    managers = []
    if data.manager_ids:
        managers = db.query(User).filter(User.id.in_(data.manager_ids)).all()

    category = Category(
        name_zh=data.name_zh,
        name_en=data.name_en,
        slug=data.slug,
        parent_id=data.parent_id,
        level=data.level,
        sort_zh=data.sort_zh,
        sort_en=data.sort_en,
        status=data.status,
        desc_zh=data.desc_zh,
        desc_en=data.desc_en,
        managers=managers,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Permission check on current category
    if not check_category_permission(db, category, current_user):
        raise HTTPException(status_code=403, detail="Permission denied to manage this category")

    # If changing parent, check permission on the new parent
    if data.parent_id is not None and data.parent_id != category.parent_id:
        if data.parent_id == 0 or data.parent_id is None:
            if current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Only admins can move categories to root")
        else:
            new_parent = db.query(Category).filter(Category.id == data.parent_id).first()
            if not new_parent:
                raise HTTPException(status_code=404, detail="New parent category not found")
            if not check_category_permission(db, new_parent, current_user):
                raise HTTPException(status_code=403, detail="Permission denied to manage the new parent category")

    if data.slug is not None and data.slug != category.slug:
        existing = db.query(Category).filter(Category.slug == data.slug).first()
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")

    # Update simple fields
    for field, value in data.model_dump(exclude={"manager_ids"}, exclude_unset=True).items():
        setattr(category, field, value)

    # Update managers if provided
    if data.manager_ids is not None:
        managers = db.query(User).filter(User.id.in_(data.manager_ids)).all()
        category.managers = managers

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Permission check
    if not check_category_permission(db, category, current_user):
        raise HTTPException(status_code=403, detail="Permission denied to delete this category")

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
