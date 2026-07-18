from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

user_bookmarks_categories = Table(
    "user_bookmarks_categories",
    Base.metadata,
    Column("bookmark_id", Integer, ForeignKey("user_bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("user_categories.id", ondelete="CASCADE"), primary_key=True),
)


class UserBookmark(Base):
    __tablename__ = "user_bookmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(2048), nullable=False, unique=True)
    favicon_url = Column(String(2048), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="user_bookmarks")
    categories = relationship("UserCategory", secondary=user_bookmarks_categories, backref="user_bookmarks")
