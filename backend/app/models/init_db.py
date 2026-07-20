from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.category import Category
from app.models.user_category import UserCategory
from app.models.bookmark import Bookmark
from app.models.user_bookmark import UserBookmark


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            first_user = db.query(User).first()
            if first_user:
                first_user.role = "admin"
                db.commit()
    finally:
        db.close()
