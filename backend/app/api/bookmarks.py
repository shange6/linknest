from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

from app.core.database import get_db
from app.core.auth import require_admin, get_current_user
from app.models.bookmark import Bookmark
from app.models.category import Category
from app.models.user import User
from app.schemas.schemas import BookmarkCreate, BookmarkUpdate, BookmarkOut, BookmarkListOut

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


def get_all_descendant_ids(db: Session, category_id: int) -> list[int]:
    """Get all descendant category IDs (including the given category_id)."""
    ids = [category_id]
    children = db.query(Category).filter(Category.parent_id == category_id).all()
    for child in children:
        ids.extend(get_all_descendant_ids(db, child.id))
    return ids


@router.get("", response_model=BookmarkListOut)
def get_bookmarks(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Bookmark)

    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        descendant_ids = get_all_descendant_ids(db, category_id)
        query = query.filter(Bookmark.categories.any(Category.id.in_(descendant_ids)))

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Bookmark.title.ilike(like)) | (Bookmark.url.ilike(like))
        )

    total = query.count()
    total_pages = max(1, ceil(total / page_size))
    if page > total_pages:
        page = total_pages

    items = (
        query.order_by(Bookmark.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return BookmarkListOut(
        items=[BookmarkOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=BookmarkOut, status_code=201)
def create_bookmark(
    data: BookmarkCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    bookmark = Bookmark(
        title=data.title,
        url=data.url,
        description=data.description,
    )
    if data.category_ids:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        bookmark.categories = categories
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.get("/{bookmark_id}", response_model=BookmarkOut)
def get_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark


@router.put("/{bookmark_id}", response_model=BookmarkOut)
def update_bookmark(
    bookmark_id: int,
    data: BookmarkUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    if data.title is not None:
        bookmark.title = data.title
    if data.url is not None:
        bookmark.url = data.url
    if data.description is not None:
        bookmark.description = data.description
    if data.category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        bookmark.categories = categories

    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.delete("/{bookmark_id}", status_code=204)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return None
