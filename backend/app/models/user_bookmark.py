from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

user_categories_bookmarks = Table(
    "user_categories_bookmarks",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("user_category_id", Integer, ForeignKey("user_categories.id", ondelete="CASCADE"), primary_key=True),
    Column("user_bookmark_id", Integer, ForeignKey("user_bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)

user_categories_global_bookmarks = Table(
    "user_categories_global_bookmarks",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("user_category_id", Integer, ForeignKey("user_categories.id", ondelete="CASCADE"), primary_key=True),
    Column("bookmark_id", Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)


class UserBookmark(Base):
    __tablename__ = "user_bookmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    href = Column(Text, nullable=False, index=True)
    icon = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", backref="user_bookmarks")
    categories = relationship("UserCategory", secondary=user_categories_bookmarks, backref="user_bookmarks")

