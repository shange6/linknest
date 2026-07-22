from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.category import Category, CategoryTranslation
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


def format_category_dict(category: Category, lang: str = "zh") -> Dict[str, Any]:
    """Format category object with translation fields for requested language and backward compatibility."""
    trans_map = {t.language_code: t for t in category.translations}
    target_t = trans_map.get(lang) or trans_map.get("zh") or (category.translations[0] if category.translations else None)

    zh_t = trans_map.get("zh")
    en_t = trans_map.get("en")

    return {
        "id": category.id,
        "slug": category.slug,
        "parent_id": category.parent_id,
        "status": category.status,
        "name": target_t.name if target_t else "",
        "description": target_t.description if target_t else None,
        "sort": target_t.sort if target_t else None,
        "name_zh": zh_t.name if zh_t else (target_t.name if target_t else ""),
        "name_en": en_t.name if en_t else None,
        "desc_zh": zh_t.description if zh_t else (target_t.description if target_t else None),
        "desc_en": en_t.description if en_t else None,
        "sort_zh": zh_t.sort if zh_t else (target_t.sort if target_t else None),
        "sort_en": en_t.sort if en_t else None,
        "created_at": category.created_at.isoformat() if category.created_at else None,
        "updated_at": category.updated_at.isoformat() if category.updated_at else None,
        "translations": [
            {
                "language_code": t.language_code,
                "name": t.name,
                "description": t.description,
                "sort": t.sort,
            }
            for t in category.translations
        ],
        "bookmarks_count": len(category.bookmarks),
        "managers": [{"id": m.id, "username": m.username, "email": m.email} for m in category.managers],
    }


def build_category_tree(categories: List[Category], parent_id: Optional[int] = None, lang: str = "zh") -> List[Dict[str, Any]]:
    """Recursively build category tree from flat list."""
    children = [c for c in categories if c.parent_id == parent_id]
    
    def sort_key(c: Category):
        node = format_category_dict(c, lang)
        return node["sort"] if node["sort"] is not None else 99999

    children.sort(key=sort_key)
    result = []
    for child in children:
        node = format_category_dict(child, lang)
        node["children"] = build_category_tree(categories, child.id, lang)
        result.append(node)
    return result


def sync_category_translations(db: Session, category: Category, data: CategoryCreate | CategoryUpdate):
    """Sync category translations from Pydantic input."""
    existing_trans = {t.language_code: t for t in category.translations}

    trans_to_process: Dict[str, Dict[str, Any]] = {}

    # Handle explicit translations list
    if data.translations is not None and len(data.translations) > 0:
        for t_item in data.translations:
            trans_to_process[t_item.language_code] = {
                "name": t_item.name,
                "description": t_item.description,
                "sort": t_item.sort,
            }
    else:
        # Backward compatibility fallback
        if getattr(data, "name_zh", None) is not None:
            trans_to_process["zh"] = {
                "name": data.name_zh,
                "description": getattr(data, "desc_zh", None),
                "sort": getattr(data, "sort_zh", None),
            }
        if getattr(data, "name_en", None) is not None:
            trans_to_process["en"] = {
                "name": data.name_en,
                "description": getattr(data, "desc_en", None),
                "sort": getattr(data, "sort_en", None),
            }

    for lang_code, values in trans_to_process.items():
        if lang_code in existing_trans:
            t_obj = existing_trans[lang_code]
            t_obj.name = values["name"]
            if values["description"] is not None:
                t_obj.description = values["description"]
            if values["sort"] is not None:
                t_obj.sort = values["sort"]
        else:
            t_obj = CategoryTranslation(
                category_id=category.id,
                language_code=lang_code,
                name=values["name"],
                description=values["description"],
                sort=values["sort"],
            )
            category.translations.append(t_obj)


@router.get("", response_model=List[Dict[str, Any]])
def get_categories(
    lang: str = Query("zh"),
    db: Session = Depends(get_db)
):
    categories = db.query(Category).all()
    return build_category_tree(categories, lang=lang)


@router.get("/{category_id}", response_model=Dict[str, Any])
def get_category(category_id: int, lang: str = Query("zh"), db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    node = format_category_dict(category, lang=lang)
    node["children"] = [format_category_dict(c, lang=lang) for c in category.children]
    return node


@router.get("/{category_id}/children", response_model=List[Dict[str, Any]])
def get_category_children(category_id: int, lang: str = Query("zh"), db: Session = Depends(get_db)):
    children = db.query(Category).filter(Category.parent_id == category_id).all()
    return [format_category_dict(c, lang=lang) for c in children]


@router.post("", response_model=Dict[str, Any], status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.id:
        existing_id = db.query(Category).filter(Category.id == data.id).first()
        if existing_id:
            raise HTTPException(status_code=400, detail="ID already exists")

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

    category_kwargs = {
        "slug": data.slug,
        "parent_id": data.parent_id,
        "status": data.status,
        "managers": managers,
    }
    if data.id:
        category_kwargs["id"] = data.id

    category = Category(**category_kwargs)
    db.add(category)
    db.flush()

    sync_category_translations(db, category, data)
    db.commit()
    db.refresh(category)
    return format_category_dict(category)


@router.put("/{category_id}", response_model=Dict[str, Any])
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if not check_category_permission(db, category, current_user):
        raise HTTPException(status_code=403, detail="Permission denied to manage this category")

    if data.id is not None and data.id != category.id:
        existing_id = db.query(Category).filter(Category.id == data.id).first()
        if existing_id:
            raise HTTPException(status_code=400, detail="Target ID already exists")
        old_id = category.id
        new_id = data.id
        db.query(Category).filter(Category.parent_id == old_id).update({"parent_id": new_id})
        category.id = new_id

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
            category.parent_id = data.parent_id

    if data.slug is not None and data.slug != category.slug:
        existing = db.query(Category).filter(Category.slug == data.slug).first()
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")
        category.slug = data.slug

    if data.status is not None:
        category.status = data.status

    if data.manager_ids is not None:
        managers = db.query(User).filter(User.id.in_(data.manager_ids)).all()
        category.managers = managers

    sync_category_translations(db, category, data)
    db.commit()
    db.refresh(category)
    return format_category_dict(category)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if not check_category_permission(db, category, current_user):
        raise HTTPException(status_code=403, detail="Permission denied to delete this category")

    _delete_children(db, category_id)
    db.delete(category)
    db.commit()
    return None


def _delete_children(db: Session, parent_id: int):
    children = db.query(Category).filter(Category.parent_id == parent_id).all()
    for child in children:
        _delete_children(db, child.id)
        db.delete(child)

