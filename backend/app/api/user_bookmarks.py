from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.user_bookmark import UserFavorite
from app.schemas.schemas import FavoriteCreate, FavoriteOut, BookmarkOut

router = APIRouter(prefix="/api/user_bookmarks", tags=["user_bookmarks"])


@router.get("", response_model=list[FavoriteOut])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    favorites = (
        db.query(UserFavorite)
        .filter(UserFavorite.user_id == current_user.id)
        .order_by(UserFavorite.created_at.desc())
        .all()
    )
    return favorites


@router.post("", response_model=FavoriteOut, status_code=201)
def add_favorite(
    data: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmark = db.query(Bookmark).filter(Bookmark.id == data.bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    existing = (
        db.query(UserFavorite)
        .filter(
            UserFavorite.user_id == current_user.id,
            UserFavorite.bookmark_id == data.bookmark_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already favorited")

    fav = UserFavorite(user_id=current_user.id, bookmark_id=data.bookmark_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


@router.delete("/{bookmark_id}", status_code=204)
def remove_favorite(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fav = (
        db.query(UserFavorite)
        .filter(
            UserFavorite.user_id == current_user.id,
            UserFavorite.bookmark_id == bookmark_id,
        )
        .first()
    )
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(fav)
    db.commit()
    return None


@router.get("/check/{bookmark_id}", response_model=dict)
def check_favorite(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fav = (
        db.query(UserFavorite)
        .filter(
            UserFavorite.user_id == current_user.id,
            UserFavorite.bookmark_id == bookmark_id,
        )
        .first()
    )
    return {"favorited": fav is not None}
