from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserFavorite(Base):
    __tablename__ = "user_bookmarks"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    bookmark_id = Column(Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="favorites")
    bookmark = relationship("Bookmark")
    tag = relationship("Tag")
