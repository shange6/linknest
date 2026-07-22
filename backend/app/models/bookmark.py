from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

categories_bookmarks = Table(
    "categories_bookmarks",
    Base.metadata,
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
    Column("bookmark_id", Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("status", Boolean, default=True, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)

bookmark_keywords = Table(
    "bookmark_keywords",
    Base.metadata,
    Column("bookmark_id", Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    href = Column(Text, nullable=False, unique=True)
    icon = Column(Text, nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    categories = relationship("Category", secondary=categories_bookmarks, backref="bookmarks")
    translations = relationship("BookmarkTranslation", cascade="all, delete-orphan", backref="bookmark")
    keywords = relationship("Keyword", secondary=bookmark_keywords, backref="bookmarks")


class BookmarkTranslation(Base):
    __tablename__ = "bookmark_translations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bookmark_id = Column(Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False)
    sort = Column(Integer, default=None, nullable=True)
    name = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, default=None, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("bookmark_id", "language_code", name="uq_bookmark_translation_lang"),
    )


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(20), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

