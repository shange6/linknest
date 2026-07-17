from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from math import ceil

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.user_click_history import UserClickHistory
from app.schemas.schemas import ClickHistoryCreate, ClickHistoryOut

router = APIRouter(prefix="/api/history", tags=["click-history"])


@router.get("", response_model=list[ClickHistoryOut])
def get_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = (
        db.query(UserClickHistory)
        .filter(UserClickHistory.user_id == current_user.id)
        .order_by(UserClickHistory.clicked_at.desc())
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

    click = UserClickHistory(
        user_id=current_user.id,
        bookmark_id=data.bookmark_id,
    )
    db.add(click)
    db.commit()
    db.refresh(click)
    return click


@router.delete("", status_code=204)
def clear_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(UserClickHistory).filter(
        UserClickHistory.user_id == current_user.id
    ).delete()
    db.commit()
    return None
