from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.user_category import UserCategory
from app.models.user_bookmark import UserBookmark
from app.schemas.schemas import UserBookmarkCreate, UserBookmarkOut
from app.core.favicon import fetch_favicon, download_and_convert_to_base64

router = APIRouter(prefix="/api/user_bookmarks", tags=["user_bookmarks"])


@router.get("", response_model=list[UserBookmarkOut])
def get_userBookmark(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmarks = (
        db.query(UserBookmark)
        .filter(UserBookmark.user_id == current_user.id)
        .order_by(UserBookmark.created_at.desc())
        .all()
    )
    return bookmarks


@router.post("", response_model=UserBookmarkOut, status_code=201)
def add_userBookmark(
    data: UserBookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(UserBookmark)
        .filter(
            UserBookmark.user_id == current_user.id,
            UserBookmark.href == data.href,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already favorited")

    categories = []
    if data.category_ids:
        categories = (
            db.query(UserCategory)
            .filter(
                UserCategory.user_id == current_user.id,
                UserCategory.id.in_(data.category_ids),
            )
            .all()
        )

    resolved_icon = data.icon
    if resolved_icon and (resolved_icon.startswith("http://") or resolved_icon.startswith("https://")):
        resolved_icon = download_and_convert_to_base64(resolved_icon)
    if not resolved_icon:
        resolved_icon = fetch_favicon(data.href)

    bookmark = UserBookmark(
        user_id=current_user.id,
        title=data.title,
        href=data.href,
        icon=resolved_icon,
        description=data.description,
        categories=categories,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.delete("/{bookmark_id}", status_code=204)
def remonv_userBookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmark = (
        db.query(UserBookmark)
        .filter(
            UserBookmark.user_id == current_user.id,
            UserBookmark.id == bookmark_id,
        )
        .first()
    )
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return None


@router.get("/check", response_model=dict)
def check_userBookmark(
    href: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmark = (
        db.query(UserBookmark)
        .filter(
            UserBookmark.user_id == current_user.id,
            UserBookmark.href == href,
        )
        .first()
    )
    return {"favorited": bookmark is not None}
