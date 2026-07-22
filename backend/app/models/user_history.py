from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserHistoryBookmark(Base):
    __tablename__ = "user_history_bookmarks"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    user_bookmark_id = Column(Integer, ForeignKey("user_bookmarks.id", ondelete="CASCADE"), primary_key=True)
    click_count = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_user_history_bookmarks_bookmark_id", "user_bookmark_id"),
    )

    user = relationship("User", backref="user_bookmark_history")
    user_bookmark = relationship("UserBookmark")


class UserHistoryGlobalBookmark(Base):
    __tablename__ = "user_history_global_bookmarks"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    bookmark_id = Column(Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True)
    click_count = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_user_history_global_bookmarks_bookmark_id", "bookmark_id"),
    )

    user = relationship("User", backref="global_bookmark_history")
    bookmark = relationship("Bookmark")

