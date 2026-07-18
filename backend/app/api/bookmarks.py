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
from app.core.favicon import fetch_favicon, download_and_convert_to_base64

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
            (Bookmark.title_zh.ilike(like)) | (Bookmark.title_en.ilike(like)) | (Bookmark.href.ilike(like))
        )

    total = query.count()
    total_pages = max(1, ceil(total / page_size))
    if page > total_pages:
        page = total_pages

    items = (
        query.order_by(
            Bookmark.sort_zh.asc().nulls_last(),
            Bookmark.sort_en.asc().nulls_last(),
            Bookmark.created_at.desc()
        )
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
    resolved_icon = data.icon
    if resolved_icon and (resolved_icon.startswith("http://") or resolved_icon.startswith("https://")):
        resolved_icon = download_and_convert_to_base64(resolved_icon)
    if not resolved_icon:
        resolved_icon = fetch_favicon(data.href)

    bookmark = Bookmark(
        title_zh=data.title_zh,
        title_en=data.title_en,
        href=data.href,
        icon=resolved_icon,
        desc_zh=data.desc_zh,
        desc_en=data.desc_en,
        status=data.status,
        sort_zh=data.sort_zh,
        sort_en=data.sort_en,
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

    if data.title_zh is not None:
        bookmark.title_zh = data.title_zh
    if data.title_en is not None:
        bookmark.title_en = data.title_en
    if data.href is not None:
        bookmark.href = data.href
    if data.icon is not None:
        resolved_icon = data.icon
        if resolved_icon and (resolved_icon.startswith("http://") or resolved_icon.startswith("https://")):
            resolved_icon = download_and_convert_to_base64(resolved_icon)
        bookmark.icon = resolved_icon
    if data.desc_zh is not None:
        bookmark.desc_zh = data.desc_zh
    if data.desc_en is not None:
        bookmark.desc_en = data.desc_en
    if data.status is not None:
        bookmark.status = data.status
    if data.sort_zh is not None:
        bookmark.sort_zh = data.sort_zh
    if data.sort_en is not None:
        bookmark.sort_en = data.sort_en
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
