from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth import require_admin
from app.models.tag import Tag
from app.models.user import User
from app.schemas.schemas import TagOut, TagCreate, TagUpdate

router = APIRouter(prefix="/api/tags", tags=["tags"])


def build_tag_tree(tags: list[Tag], parent_id: Optional[int] = None) -> list[dict]:
    """Recursively build tag tree from flat list."""
    children = [t for t in tags if t.parent_id == parent_id]
    children.sort(key=lambda x: x.sort_order)
    result = []
    for child in children:
        node = {
            "id": child.id,
            "name": child.name,
            "slug": child.slug,
            "parent_id": child.parent_id,
            "level": child.level,
            "sort_order": child.sort_order,
            "description": child.description,
            "updated_at": child.updated_at.isoformat() if child.updated_at else None,
            "children": build_tag_tree(tags, child.id),
        }
        result.append(node)
    return result


@router.get("", response_model=list[dict])
def get_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).order_by(Tag.level, Tag.sort_order).all()
    return build_tag_tree(tags)


@router.get("/{tag_id}", response_model=TagOut)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/{tag_id}/children", response_model=list[TagOut])
def get_tag_children(tag_id: int, db: Session = Depends(get_db)):
    children = db.query(Tag).filter(Tag.parent_id == tag_id).order_by(Tag.sort_order).all()
    return children


# --- Admin tag management ---
@router.post("", response_model=TagOut, status_code=201)
def create_tag(
    data: TagCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = db.query(Tag).filter(Tag.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    if data.parent_id:
        parent = db.query(Tag).filter(Tag.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent tag not found")
    tag = Tag(**data.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.put("/{tag_id}", response_model=TagOut)
def update_tag(
    tag_id: int,
    data: TagUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if data.slug is not None and data.slug != tag.slug:
        existing = db.query(Tag).filter(Tag.slug == data.slug).first()
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tag, field, value)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    # Recursively delete all descendants
    _delete_children(db, tag_id)
    db.delete(tag)
    db.commit()
    return None


def _delete_children(db: Session, parent_id: int):
    children = db.query(Tag).filter(Tag.parent_id == parent_id).all()
    for child in children:
        _delete_children(db, child.id)
        db.delete(child)
