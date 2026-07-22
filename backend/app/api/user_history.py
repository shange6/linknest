from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.user_bookmark import UserBookmark
from app.models.user_history import UserHistoryBookmark, UserHistoryGlobalBookmark
from app.schemas.schemas import ClickHistoryCreate
from app.api.bookmarks import format_bookmark_dict
from app.api.user_bookmarks import format_user_bookmark

router = APIRouter(prefix="/api/user_history", tags=["user_history"])


@router.get("", response_model=List[Dict[str, Any]])
def get_history(
    limit: int = Query(50, ge=1, le=200),
    lang: str = Query("zh"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    global_hist = (
        db.query(UserHistoryGlobalBookmark)
        .filter(UserHistoryGlobalBookmark.user_id == current_user.id)
        .order_by(UserHistoryGlobalBookmark.updated_at.desc())
        .limit(limit)
        .all()
    )
    user_hist = (
        db.query(UserHistoryBookmark)
        .filter(UserHistoryBookmark.user_id == current_user.id)
        .order_by(UserHistoryBookmark.updated_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for h in global_hist:
        result.append({
            "user_id": h.user_id,
            "bookmark_id": h.bookmark_id,
            "user_bookmark_id": None,
            "bookmark": format_bookmark_dict(h.bookmark, lang=lang) if h.bookmark else None,
            "user_bookmark": None,
            "click_count": h.click_count,
            "created_at": h.created_at,
            "updated_at": h.updated_at,
        })
    for h in user_hist:
        result.append({
            "user_id": h.user_id,
            "bookmark_id": None,
            "user_bookmark_id": h.user_bookmark_id,
            "bookmark": None,
            "user_bookmark": format_user_bookmark(h.user_bookmark) if h.user_bookmark else None,
            "click_count": h.click_count,
            "created_at": h.created_at,
            "updated_at": h.updated_at,
        })

    result.sort(key=lambda x: x["updated_at"], reverse=True)
    return result[:limit]


@router.post("", response_model=Dict[str, Any], status_code=201)
def record_click(
    data: ClickHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.user_bookmark_id or not data.is_global:
        bm_id = data.user_bookmark_id or data.bookmark_id
        ub = db.query(UserBookmark).filter(UserBookmark.id == bm_id, UserBookmark.user_id == current_user.id).first()
        if not ub:
            raise HTTPException(status_code=404, detail="User bookmark not found")

        existing = (
            db.query(UserHistoryBookmark)
            .filter(
                UserHistoryBookmark.user_id == current_user.id,
                UserHistoryBookmark.user_bookmark_id == ub.id,
            )
            .first()
        )
        if existing:
            existing.click_count += 1
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return {
                "user_id": existing.user_id,
                "user_bookmark_id": existing.user_bookmark_id,
                "click_count": existing.click_count,
                "updated_at": existing.updated_at,
            }
        else:
            record = UserHistoryBookmark(user_id=current_user.id, user_bookmark_id=ub.id)
            db.add(record)
            db.commit()
            db.refresh(record)
            return {
                "user_id": record.user_id,
                "user_bookmark_id": record.user_bookmark_id,
                "click_count": record.click_count,
                "updated_at": record.updated_at,
            }
    else:
        bm = db.query(Bookmark).filter(Bookmark.id == data.bookmark_id).first()
        if not bm:
            raise HTTPException(status_code=404, detail="Bookmark not found")

        existing = (
            db.query(UserHistoryGlobalBookmark)
            .filter(
                UserHistoryGlobalBookmark.user_id == current_user.id,
                UserHistoryGlobalBookmark.bookmark_id == bm.id,
            )
            .first()
        )
        if existing:
            existing.click_count += 1
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return {
                "user_id": existing.user_id,
                "bookmark_id": existing.bookmark_id,
                "click_count": existing.click_count,
                "updated_at": existing.updated_at,
            }
        else:
            record = UserHistoryGlobalBookmark(user_id=current_user.id, bookmark_id=bm.id)
            db.add(record)
            db.commit()
            db.refresh(record)
            return {
                "user_id": record.user_id,
                "bookmark_id": record.bookmark_id,
                "click_count": record.click_count,
                "updated_at": record.updated_at,
            }


@router.delete("", status_code=204)
def clear_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(UserHistoryGlobalBookmark).filter(UserHistoryGlobalBookmark.user_id == current_user.id).delete()
    db.query(UserHistoryBookmark).filter(UserHistoryBookmark.user_id == current_user.id).delete()
    db.commit()
    return None

