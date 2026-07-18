from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

bookmark_categories = Table(
    "bookmarks_categories",
    Base.metadata,
    Column("bookmark_id", Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title_zh = Column(String(500), nullable=False)
    title_en = Column(String(500), nullable=True)
    href = Column(String(2048), nullable=False, unique=True)
    icon = Column(Text, nullable=True)
    desc_zh = Column(Text, nullable=True)
    desc_en = Column(Text, nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    sort_zh = Column(Integer, default=None, nullable=True)
    sort_en = Column(Integer, default=None, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    categories = relationship("Category", secondary=bookmark_categories, backref="bookmarks")
