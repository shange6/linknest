from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.user_history import UserHistory
from app.schemas.schemas import ClickHistoryCreate, ClickHistoryOut

router = APIRouter(prefix="/api/history", tags=["click-history"])


@router.get("", response_model=list[ClickHistoryOut])
def get_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = (
        db.query(UserHistory)
        .filter(UserHistory.user_id == current_user.id)
        .order_by(UserHistory.updated_at.desc())
        .limit(limit)
        .all()
    )
    return history


@router.post("", response_model=ClickHistoryOut, status_code=201)
def record_click(
    data: ClickHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmark = db.query(Bookmark).filter(Bookmark.id == data.bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    existing = (
        db.query(UserHistory)
        .filter(
            UserHistory.user_id == current_user.id,
            UserHistory.bookmark_id == data.bookmark_id,
        )
        .first()
    )
    if existing:
        existing.click_count += 1
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    record = UserHistory(
        user_id=current_user.id,
        bookmark_id=data.bookmark_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("", status_code=204)
def clear_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(UserHistory).filter(
        UserHistory.user_id == current_user.id
    ).delete()
    db.commit()
    return None
