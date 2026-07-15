import sys
sys.path.insert(0, r"C:\Users\shange\.openclaw-autoclaw\workspace\linknest\backend")

from app.core.database import SessionLocal, engine
from app.core.auth import get_password_hash
from app.models.user import User
from app.models.tag import Tag
from app.models.bookmark import Bookmark
from app.models.init_db import Base

# Recreate tables
Base.metadata.create_all(bind=engine)

# Import tags from seed
import json, os
json_path = os.path.join(os.path.dirname(__file__), "seed_data", "tags.json")
with open(json_path, "r", encoding="utf-8") as f:
    tag_data = json.load(f)

db = SessionLocal()

def import_tags(items, parent_id=None):
    for item in items:
        children = item.pop("children", [])
        tag = Tag(parent_id=parent_id, **item)
        db.add(tag)
        db.flush()
        import_tags(children, parent_id=tag.id)

import_tags(tag_data)
print(f"Tags imported: {db.query(Tag).count()}")

# Create users
u1 = User(email="shange@linknest.local", username="shange", password=get_password_hash("admin123"), role="admin")
u2 = User(email="normal@test.com", username="normal", password=get_password_hash("user1234"), role="user")
db.add_all([u1, u2])
db.commit()
print(f"Admin: id={u1.id} role={u1.role}")
print(f"Normal: id={u2.id} role={u2.role}")
db.close()
print("Done.")
