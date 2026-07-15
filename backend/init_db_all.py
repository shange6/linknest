import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.core.auth import get_password_hash
from app.models.init_db import Base
from app.models.tag import Tag
from app.models.user import User

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Import seed tags
json_path = os.path.join(os.path.dirname(__file__), "seed_data", "tags.json")
with open(json_path, "r", encoding="utf-8") as f:
    seed_data = json.load(f)

def import_seed(items, parent_id=None):
    for item in items:
        children = item.pop("children", [])
        tag = Tag(parent_id=parent_id, **item)
        db.add(tag)
        db.flush()
        import_seed(children, parent_id=tag.id)

import_seed(seed_data)
db.commit()
print(f"Seed tags: {db.query(Tag).count()}")

# Users
u1 = User(email="shange@linknest.local", username="shange", password=get_pa…ash("admin123"), role="admin")
u2 = User(email="normal@test.com", username="normal", password=get_pa…ash("user1234"), role="user")
db.add_all([u1, u2])
db.commit()
db.close()
print("DB initialized with users.")
