from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserTag(Base):
    __tablename__ = "user_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("user_tags.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_user_tag_slug"),
    )

    user = relationship("User", backref="user_tags")
    parent = relationship("UserTag", remote_side=[id], backref="children")
