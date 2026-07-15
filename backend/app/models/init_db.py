from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.tag import Tag
from app.models.bookmark import Bookmark


def init_db():
    Base.metadata.create_all(bind=engine)
