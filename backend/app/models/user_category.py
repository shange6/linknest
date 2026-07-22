from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserCategory(Base):
    __tablename__ = "user_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("user_categories.id"), nullable=True)
    sort = Column(Integer, default=None, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_user_category_slug"),
        CheckConstraint("slug NOT GLOB '*[^a-z0-9-]*'", name="ck_user_categories_slug_format"),
    )

    user = relationship("User", backref="user_categories")
    parent = relationship("UserCategory", remote_side=[id], backref="children")
    global_bookmarks = relationship("Bookmark", secondary="user_categories_global_bookmarks", backref="user_categories")

