from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserHistory(Base):
    __tablename__ = "user_history"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    bookmark_id = Column(Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True)
    click_count = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_history_user_count", "user_id", "click_count"),
    )

    user = relationship("User", backref="click_history")
    bookmark = relationship("Bookmark")
