from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, CheckConstraint, Table, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

category_managers = Table(
    "category_managers",
    Base.metadata,
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("status", Boolean, default=True, nullable=False),
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_zh = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_zh = Column(Integer, default=None, nullable=True)
    sort_en = Column(Integer, default=None, nullable=True)
    desc_zh = Column(Text, nullable=True)
    desc_en = Column(Text, nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("slug NOT GLOB '*[^a-zA-Z0-9-]*'", name="ck_categories_slug_format"),
    )

    parent = relationship("Category", remote_side=[id], backref="children")
    managers = relationship(
        "User",
        secondary=category_managers,
        primaryjoin="and_(Category.id==category_managers.c.category_id, category_managers.c.status==1)",
        secondaryjoin="User.id==category_managers.c.user_id",
        backref="managed_categories"
    )
